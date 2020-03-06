import base64
import threading
import time
import zlib

from .constant import (ACTIVITY_STATE_KEY, BRIGHTNESS_KEY,
                       CAPTURED_TODAY_KEY, FLIP_KEY, IDLE_SNAPSHOT_PATH, LAST_CAPTURE_KEY,
                       CRY_DETECTION_KEY, LIGHT_BRIGHTNESS_KEY, LIGHT_MODE_KEY,
                       LAST_IMAGE_DATA_KEY, LAST_IMAGE_KEY, LAMP_STATE_KEY,
                       LAST_IMAGE_SRC_KEY, MEDIA_COUNT_KEY,
                       MEDIA_UPLOAD_KEYS, MIRROR_KEY, MOTION_SENS_KEY,
                       POWER_SAVE_KEY, PRELOAD_DAYS, PRIVACY_KEY,
                       RECORD_START_PATH, RECORD_STOP_PATH,
                       SNAPSHOT_KEY, SIREN_STATE_KEY, STREAM_SNAPSHOT_KEY,
                       STREAM_SNAPSHOT_PATH, STREAM_START_PATH, CAMERA_MEDIA_DELAY,
                       AUDIO_POSITION_KEY, AUDIO_TRACK_KEY, DEFAULT_TRACK_ID, MEDIA_PLAYER_RESOURCE_ID)
from .device import ArloChildDevice
from .util import http_get, http_get_img


class ArloCamera(ArloChildDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._recent = False
        self._recent_job = None
        self._cache_count = None
        self._cached_videos = None
        self._min_days_vdo_cache = PRELOAD_DAYS
        self._lock = threading.Condition()
        self._snapshot_state = 'idle'
        self._clear_snapshot_cb = None
        self._arlo.bg.run_in(self._update_media, CAMERA_MEDIA_DELAY)

    def _set_recent(self, timeo):
        with self._lock:
            self._recent = True
            self._arlo.bg.cancel(self._recent_job)
            self._recent_job = self._arlo.bg.run_in(self._clear_recent, timeo)
        self._arlo.debug('turning recent ON for ' + self._name)
        self._do_callbacks('recentActivity', True)

    def _clear_recent(self):
        with self._lock:
            self._recent = False
            self._recent_job = None
        self._arlo.debug('turning recent OFF for ' + self._name)
        self._do_callbacks('recentActivity', False)

    # media library finished. Update our counts
    def _update_media(self):
        self._arlo.debug('reloading cache for ' + self._name)
        count, videos = self._arlo.ml.videos_for(self)
        if videos:
            captured_today = len([video for video in videos if video.created_today])
            last_captured = videos[0].created_at_pretty(self._arlo.cfg.last_format)
        else:
            captured_today = 0
            last_captured = None

        # update local copies
        with self._lock:
            self._cache_count = count
            self._cached_videos = videos

        # signal video up!
        self._save_and_do_callbacks(CAPTURED_TODAY_KEY, captured_today)
        if last_captured is not None:
            self._save_and_do_callbacks(LAST_CAPTURE_KEY, last_captured)
        self._do_callbacks('mediaUploadNotification', True)

    def _clear_snapshot(self):
        # signal to anybody waiting
        with self._lock:
            if self._snapshot_state != 'idle':
                self._arlo.debug('our snapshot finished, signal real state')
                self._snapshot_state = 'idle'
                self._lock.notify_all()

        # signal real mode, safe to call multiple times
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY,
                                    self._arlo.st.get([self._device_id, ACTIVITY_STATE_KEY], 'unknown'))

    def _update_media_and_thumbnail(self):
        self._arlo.debug('getting media image for ' + self.name)
        self._update_media()
        url = None
        with self._lock:
            if self._cached_videos:
                url = self._cached_videos[0].thumbnail_url
        if url is not None:
            self._save(LAST_IMAGE_KEY, url)
            self._update_last_image()

    def _update_last_image(self):
        self._arlo.debug('getting image for ' + self.name)

        # Get image and date, if fails set to blank.
        img, date = http_get_img(self._arlo.st.get([self.device_id, LAST_IMAGE_KEY], None))
        if img is None:
            self._arlo.debug('using blank image for ' + self.name)
            img = self._arlo.blank_image

        # signal up if needed
        date = date.strftime(self._arlo.cfg.last_format)
        self._save(LAST_IMAGE_SRC_KEY, 'capture/' + date)
        self._save_and_do_callbacks(LAST_CAPTURE_KEY, date)
        self._save_and_do_callbacks(LAST_IMAGE_DATA_KEY, img)

        # handle snapshot not being handled...
        self._clear_snapshot()

    def _update_last_image_from_snapshot(self):
        self._arlo.debug('getting image for ' + self.name)

        # Get image and date, if fails ignore.
        img, date = http_get_img(self._arlo.st.get([self.device_id, SNAPSHOT_KEY], None))
        if img is not None:
            date = date.strftime(self._arlo.cfg.last_format)
            self._save(LAST_IMAGE_SRC_KEY, 'snapshot/' + date)
            self._save_and_do_callbacks(LAST_IMAGE_DATA_KEY, img)

        # handle snapshot finished
        self._clear_snapshot()

    def _parse_statistic(self, data, scale):
        """Parse binary statistics returned from the history API"""
        i = 0
        for byte in bytearray(data):
            i = (i << 8) + byte

        if i == 32768:
            return None

        if scale == 0:
            return i

        return float(i) / (scale * 10)

    def _decode_sensor_data(self, properties):
        """Decode, decompress, and parse the data from the history API"""
        b64_input = ""
        for s in properties.get('payload', []):
            # pylint: disable=consider-using-join
            b64_input += s
        if b64_input == "":
            return None

        decoded = base64.b64decode(b64_input)
        data = zlib.decompress(decoded)
        points = []
        i = 0

        while i < len(data):
            points.append({
                'timestamp': int(1e3 * self._parse_statistic(data[i:(i + 4)], 0)),
                'temperature': self._parse_statistic(data[(i + 8):(i + 10)], 1),
                'humidity': self._parse_statistic(data[(i + 14):(i + 16)], 1),
                'airQuality': self._parse_statistic(data[(i + 20):(i + 22)], 1)
            })
            i += 22

        return points[-1]

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' CAMERA got one ' + resource)

        # stream has stopped or recording has stopped
        if resource == 'mediaUploadNotification':

            # look for all possible keys
            for key in MEDIA_UPLOAD_KEYS:
                value = event.get(key, None)
                if value is not None:
                    self._save_and_do_callbacks(key, value)

            # catch this one, update URL if passed in notification
            if LAST_IMAGE_KEY in event:
                self._arlo.debug(self.name + ' thumbnail changed')
                self.update_last_image()

            # recording stopped then reload library
            if event.get('recordingStopped', False):
                self._arlo.debug('recording stopped, updating library')
                self._arlo.ml.queue_update(self._update_media)

            # snapshot happened?
            value = event.get(STREAM_SNAPSHOT_KEY, '')
            if '/snapshots/' in value:
                self._arlo.debug('our snapshot finished, downloading it')
                self._save(SNAPSHOT_KEY, value)
                self._arlo.bg.run_low(self._update_last_image_from_snapshot)

            # something just happened!
            self._set_recent(self._arlo.cfg.recent_time)

            return

        # no media uploads and stream stopped?
        if self._arlo.cfg.no_media_upload:
            if event.get('properties', {}).get('activityState', 'unknown') == 'idle' and self.is_recording:
                self._arlo.debug('got a stream stop')
                self._arlo.bg.run_in(self._arlo.ml.queue_update, 5, cb=self._update_media_and_thumbnail)

        # get it an update last image
        if event.get('action', '') == 'fullFrameSnapshotAvailable':
            value = event.get('properties', {}).get('presignedFullFrameSnapshotUrl', None)
            if value is not None:
                self._arlo.debug('queing snapshot update')
                self._save(SNAPSHOT_KEY, value)
                self._arlo.bg.run_low(self._update_last_image_from_snapshot)

        # ambient sensors update
        if resource.endswith('/ambientSensors/history'):
            data = self._decode_sensor_data(event.get('properties', {}))
            if data is not None:
                self._save_and_do_callbacks('temperature', data.get('temperature'))
                self._save_and_do_callbacks('humidity', data.get('humidity'))
                self._save_and_do_callbacks('airQuality', data.get('airQuality'))

        # night light
        nightlight = event.get("properties", {}).get("nightLight", None)
        if nightlight is not None:
            self._arlo.debug("got a night light {}".format(nightlight.get("enabled", False)))
            if nightlight.get("enabled", False) is True:
                self._save_and_do_callbacks(LAMP_STATE_KEY, "on")
            else:
                self._save_and_do_callbacks(LAMP_STATE_KEY, "off")

            brightness = nightlight.get("brightness")
            if brightness is not None:
                self._save_and_do_callbacks(LIGHT_BRIGHTNESS_KEY, brightness)

            mode = nightlight.get("mode")
            if mode is not None:
                rgb = nightlight.get("rgb")
                temperature = nightlight.get("temperature")

                light_mode = {
                    'mode': mode
                }

                if rgb is not None:
                    light_mode['rgb'] = rgb
                if temperature is not None:
                    light_mode['temperature'] = temperature

                self._save_and_do_callbacks(LIGHT_MODE_KEY, light_mode)

        # audio analytics
        audioanalytics = event.get("properties", {}).get("audioAnalytics", None)
        if audioanalytics is not None:
            if audioanalytics.get(CRY_DETECTION_KEY, {}).get("triggered") is True:
                self._save_and_do_callbacks(CRY_DETECTION_KEY, "on")
            else:
                self._save_and_do_callbacks(CRY_DETECTION_KEY, "off")

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        return "cameras"

    @property
    def last_image(self):
        return self._arlo.st.get([self._device_id, LAST_IMAGE_KEY], None)

    # fill this out...
    @property
    def last_image_from_cache(self):
        return self._arlo.st.get([self._device_id, LAST_IMAGE_DATA_KEY], self._arlo.blank_image)

    @property
    def last_image_source(self):
        return self._arlo.st.get([self._device_id, LAST_IMAGE_SRC_KEY], '')

    @property
    def last_video(self):
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[0]
        return None

    def last_n_videos(self, count):
        with self._lock:
            if self._cached_videos:
                return self._cached_videos[:count]
        return []

    @property
    def last_capture(self):
        return self._arlo.st.get([self._device_id, LAST_CAPTURE_KEY], None)

    @property
    def last_capture_date_format(self):
        return self._arlo.cfg.last_format

    @property
    def brightness(self):
        return self._arlo.st.get([self._device_id, BRIGHTNESS_KEY], None)

    @property
    def flip_state(self):
        return self._arlo.st.get([self._device_id, FLIP_KEY], None)

    @property
    def mirror_state(self):
        return self._arlo.st.get([self._device_id, MIRROR_KEY], None)

    @property
    def motion_detection_sensitivity(self):
        return self._arlo.st.get([self._device_id, MOTION_SENS_KEY], None)

    @property
    def powersave_mode(self):
        return self._arlo.st.get([self._device_id, POWER_SAVE_KEY], None)

    @property
    def unseen_videos(self):
        return self._arlo.st.get([self._device_id, MEDIA_COUNT_KEY], 0)

    @property
    def captured_today(self):
        return self._arlo.st.get([self._device_id, CAPTURED_TODAY_KEY], 0)

    @property
    def min_days_vdo_cache(self):
        return self._min_days_vdo_cache

    @property
    def recent(self):
        return self._recent

    @min_days_vdo_cache.setter
    def min_days_vdo_cache(self, value):
        self._min_days_vdo_cache = value

    def update_media(self):
        """ Get latest list of recordings from the backend server. """
        self._arlo.debug('queing media update')
        self._arlo.bg.run_low(self._update_media)

    def update_last_image(self):
        """ Get last thumbnail from the backend server. """
        self._arlo.debug('queing image update')
        self._arlo.bg.run_low(self._update_last_image)

    def update_ambient_sensors(self):
        if self.model_id == 'ABC1000':
            self._arlo.bg.run(self._arlo.be.notify,
                              base=self.base_station,
                              body={"action": "get",
                                    "resource": 'cameras/{}/ambientSensors/history'.format(self.device_id),
                                    "publishResponse": False})

    def has_capability(self, cap):
        if cap in 'motionDetected':
            return True
        if cap in ('last_capture', 'captured_today', 'recent_activity', 'battery_level', 'signal_strength'):
            return True
        if cap in ('temperature', 'humidity', 'air_quality', 'airQuality') and self.model_id == 'ABC1000':
            return True
        if cap in ('audio', 'audioDetected', 'sound'):
            if self.model_id.startswith('VMC4030') or self.model_id.startswith('VMC5040') or self.model_id.startswith(
                    'VMC4040') or self.model_id == 'ABC1000':
                return True
            if self.device_type.startswith('arloq'):
                return True
        if cap in 'siren':
            if self.model_id.startswith('VMC5040') or self.model_id.startswith('VMC4040'):
                return True
        if cap in 'mediaPlayer' and self.model_id == 'ABC1000':
            return True
        if cap in 'nightLight' and self.model_id.startswith("ABC1000"):
            return True
        if cap in 'babyCryDetection' and self.model_id.startswith("ABC1000"):
            return True
        return super().has_capability(cap)

    def take_streaming_snapshot(self):
        body = {
            'xcloudId': self.xcloud_id,
            'parentId': self.parent_id,
            'deviceId': self.device_id,
            'olsonTimeZone': self.timezone,
        }
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY, 'fullFrameSnapshot')
        self._arlo.bg.run(self._arlo.be.post, path=STREAM_SNAPSHOT_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

    def take_idle_snapshot(self):
        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState': 'fullFrameSnapshot'},
            'publishResponse': True,
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo.be.gen_trans_id()
        }
        self._arlo.bg.run(self._arlo.be.post, path=IDLE_SNAPSHOT_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

    def _request_snapshot(self):
        if self._snapshot_state == 'idle':
            if self.is_streaming or self.is_recording:
                self._arlo.debug('streaming snapshot')
                self.take_streaming_snapshot()
                self._snapshot_state = 'streaming-snapshot'
            elif not self.is_taking_snapshot:
                self.take_idle_snapshot()
                self._arlo.debug('idle snapshot')
                self._snapshot_state = 'snapshot'
            self._arlo.debug('handle dodgy cameras')
            self._arlo.bg.run_in(self._clear_snapshot, 45)

    def request_snapshot(self):
        with self._lock:
            self._request_snapshot()

    def get_snapshot(self, timeout=30):
        with self._lock:
            self._request_snapshot()
            mnow = time.monotonic()
            mend = mnow + timeout
            while mnow < mend and self._snapshot_state != 'idle':
                self._lock.wait(mend - mnow)
                mnow = time.monotonic()
        return self.last_image_from_cache

    @property
    def is_taking_snapshot(self):
        if self._snapshot_state != 'idle':
            return True
        return self._arlo.st.get([self._device_id, ACTIVITY_STATE_KEY], 'unknown') == 'fullFrameSnapshot'

    @property
    def is_recording(self):
        return self._arlo.st.get([self._device_id, ACTIVITY_STATE_KEY], 'unknown') == 'alertStreamActive'

    @property
    def is_streaming(self):
        return self._arlo.st.get([self._device_id, ACTIVITY_STATE_KEY], 'unknown') == 'userStreamActive'

    @property
    def was_recently_active(self):
        return self._recent

    @property
    def state(self):
        if self.is_taking_snapshot:
            return 'taking snapshot'
        if self.is_recording:
            return 'recording'
        if self.is_streaming:
            return 'streaming'
        if self.was_recently_active:
            return 'recently active'
        return super().state

    def get_stream(self):
        body = {
            'action': 'set',
            'from': self.web_id,
            'properties': {'activityState': 'startUserStream', 'cameraId': self.device_id},
            'publishResponse': True,
            'responseUrl': '',
            'resource': self.resource_id,
            'to': self.parent_id,
            'transId': self._arlo.be.gen_trans_id()
        }
        reply = self._arlo.be.post(STREAM_START_PATH, body, headers={"xcloudId": self.xcloud_id})
        if reply is None:
            return None
        url = reply['url'].replace("rtsp://", "rtsps://")
        self._arlo.debug('url={}'.format(url))
        return url

    def get_video(self):
        video = self.last_video
        if video is not None:
            return http_get(video.video_url)
        return None

    def stop_activity(self):
        self._arlo.bg.run(self._arlo.be.notify,
                          base=self.base_station,
                          body={
                              'action': 'set',
                              'properties': {'activityState': 'idle'},
                              'publishResponse': True,
                              'resource': self.resource_id,
                          })
        return True

    def start_recording(self, duration=None):
        body = {
            'parentId': self.parent_id,
            'deviceId': self.device_id,
            'olsonTimeZone': self.timezone,
        }
        self._arlo.debug('starting recording')
        self._save_and_do_callbacks(ACTIVITY_STATE_KEY, 'alertStreamActive')
        self._arlo.bg.run(self._arlo.be.post, path=RECORD_START_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})
        if duration is not None:
            self._arlo.debug('queueing stop')
            self._arlo.bg.run_in(self.stop_recording)

    def stop_recording(self):
        body = {
            'parentId': self.parent_id,
            'deviceId': self.device_id,
        }
        self._arlo.debug('stopping recording')
        self._arlo.bg.run(self._arlo.be.post, path=RECORD_STOP_PATH, params=body,
                          headers={"xcloudId": self.xcloud_id})

    @property
    def siren_resource_id(self):
        return "siren/{}".format(self.device_id)

    @property
    def siren_state(self):
        return self._arlo.st.get([self._device_id, SIREN_STATE_KEY], "off")

    def siren_on(self, duration=300, volume=8):
        body = {
            'action': 'set',
            'resource': self.siren_resource_id,
            'publishResponse': True,
            'properties': {'sirenState': 'on', 'duration': int(duration), 'volume': int(volume), 'pattern': 'alarm'}
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def siren_off(self):
        body = {
            'action': 'set',
            'resource': self.siren_resource_id,
            'publishResponse': True,
            'properties': {'sirenState': 'off'}
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    @property
    def is_on(self):
        return not self._arlo.st.get([self._device_id, PRIVACY_KEY], False)

    def turn_on(self):
        self._arlo.bg.run(self._arlo.be.async_on_off, base=self.base_station, device=self, privacy_on=False)

    def turn_off(self):
        self._arlo.bg.run(self._arlo.be.async_on_off, base=self.base_station, device=self, privacy_on=True)

    def get_audio_playback_status(self):
        """Gets the current playback status and available track list"""
        body = {
            'action': 'get',
            'publishResponse': True,
            'resource': 'audioPlayback'
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def play_track(self, track_id=DEFAULT_TRACK_ID, position=0):
        body = {
            'action': 'playTrack',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
            'properties': {
                AUDIO_TRACK_KEY: track_id,
                AUDIO_POSITION_KEY: position
            }
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def pause_track(self):
        body = {
            'action': 'pause',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def previous_track(self):
        """Skips to the previous track in the playlist."""
        body = {
            'action': 'prevTrack',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def next_track(self):
        """Skips to the next track in the playlist."""
        body = {
            'action': 'nextTrack',
            'publishResponse': True,
            'resource': MEDIA_PLAYER_RESOURCE_ID,
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def set_music_loop_mode_continuous(self):
        """Sets the music loop mode to repeat the entire playlist."""
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'loopbackMode': 'continuous'
                }
            }
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def set_music_loop_mode_single(self):
        """Sets the music loop mode to repeat the current track."""
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'loopbackMode': 'singleTrack'
                }
            }
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def set_shuffle(self, shuffle=True):
        """Sets playback to shuffle."""
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': 'audioPlayback/config',
            'properties': {
                'config': {
                    'shuffleActive': shuffle
                }
            }
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def set_volume(self, mute=False, volume=50):
        """Sets the music volume (0-100)"""
        body = {
            'action': 'set',
            'publishResponse': True,
            'resource': self.resource_id,
            'properties': {
                'speaker': {
                    'mute': mute,
                    'volume': volume
                }
            }
        }
        self._arlo.bg.run(self._arlo.be.notify, base=self, body=body)

    def _set_nightlight_properties(self, properties):
        self._arlo.debug('{}: setting nightlight properties: {}'.format(self._name, properties))
        self._arlo.bg.run(self._arlo.be.notify,
                          base=self.base_station,
                          body={
                              'action': 'set',
                              'properties': {
                                  'nightLight': properties
                              },
                              'publishResponse': True,
                              'resource': self.resource_id,
                          })
        return True

    def nightlight_on(self):
        """Turns the nightlight on."""
        return self._set_nightlight_properties({
            'enabled': True
        })

    def nightlight_off(self):
        """Turns the nightlight off."""
        return self._set_nightlight_properties({
            'enabled': False
        })

    def set_nightlight_brightness(self, brightness):
        """Turns the nightlight brightness value (0-255)."""
        return self._set_nightlight_properties({
            'brightness': brightness
        })

    def set_nightlight_rgb(self, red=255, green=255, blue=255):
        """Turns the nightlight color to the specified RGB value."""
        return self._set_nightlight_properties({
            'mode': 'rgb',
            'rgb': {'red': red, 'green': green, 'blue': blue}
        })

    def set_nightlight_color_temperature(self, temperature):
        """Turns the nightlight to the specified Kelvin color temperature."""
        return self._set_nightlight_properties({
            'mode': 'temperature',
            'temperature': str(temperature)
        })

    def set_nightlight_mode(self, mode):
        """Turns the nightlight to a particular mode (rgb, temperature, rainbow)."""
        return self._set_nightlight_properties({
            'mode': mode
        })
