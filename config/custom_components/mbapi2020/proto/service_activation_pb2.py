# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service-activation.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='service-activation.proto',
  package='proto',
  syntax='proto3',
  serialized_options=b'\n\032com.daimler.mbcarkit.proto\220\001\001',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x18service-activation.proto\x12\x05proto\"?\n$AcknowledgeServiceStatusUpdatesByVIN\x12\x17\n\x0fsequence_number\x18\x01 \x01(\x05\"9\n\x1e\x41\x63knowledgeServiceStatusUpdate\x12\x17\n\x0fsequence_number\x18\x01 \x01(\x05\"\xc0\x01\n\x19ServiceStatusUpdatesByVIN\x12\x17\n\x0fsequence_number\x18\x01 \x01(\x05\x12>\n\x07updates\x18\x02 \x03(\x0b\x32-.proto.ServiceStatusUpdatesByVIN.UpdatesEntry\x1aJ\n\x0cUpdatesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.proto.ServiceStatusUpdate:\x02\x38\x01\"\x82\x02\n\x13ServiceStatusUpdate\x12\x17\n\x0fsequence_number\x18\x01 \x01(\x05\x12\x0f\n\x07\x63iam_id\x18\x07 \x01(\t\x12\x0b\n\x03vin\x18\x05 \x01(\t\x12\x16\n\x0e\x65mit_timestamp\x18\x02 \x01(\x03\x12\x1c\n\x14\x65mit_timestamp_in_ms\x18\x08 \x01(\x03\x12\x38\n\x07updates\x18\x06 \x03(\x0b\x32\'.proto.ServiceStatusUpdate.UpdatesEntry\x1a\x44\n\x0cUpdatesEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12#\n\x05value\x18\x02 \x01(\x0e\x32\x14.proto.ServiceStatus:\x02\x38\x01*\xb3\x01\n\rServiceStatus\x12\x1a\n\x16SERVICE_STATUS_UNKNOWN\x10\x00\x12\x19\n\x15SERVICE_STATUS_ACTIVE\x10\x01\x12\x1b\n\x17SERVICE_STATUS_INACTIVE\x10\x02\x12%\n!SERVICE_STATUS_ACTIVATION_PENDING\x10\x03\x12\'\n#SERVICE_STATUS_DEACTIVATION_PENDING\x10\x04\x42\x1f\n\x1a\x63om.daimler.mbcarkit.proto\x90\x01\x01\x62\x06proto3'
)

_SERVICESTATUS = _descriptor.EnumDescriptor(
  name='ServiceStatus',
  full_name='proto.ServiceStatus',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SERVICE_STATUS_UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SERVICE_STATUS_ACTIVE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SERVICE_STATUS_INACTIVE', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SERVICE_STATUS_ACTIVATION_PENDING', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SERVICE_STATUS_DEACTIVATION_PENDING', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=616,
  serialized_end=795,
)
_sym_db.RegisterEnumDescriptor(_SERVICESTATUS)

ServiceStatus = enum_type_wrapper.EnumTypeWrapper(_SERVICESTATUS)
SERVICE_STATUS_UNKNOWN = 0
SERVICE_STATUS_ACTIVE = 1
SERVICE_STATUS_INACTIVE = 2
SERVICE_STATUS_ACTIVATION_PENDING = 3
SERVICE_STATUS_DEACTIVATION_PENDING = 4



_ACKNOWLEDGESERVICESTATUSUPDATESBYVIN = _descriptor.Descriptor(
  name='AcknowledgeServiceStatusUpdatesByVIN',
  full_name='proto.AcknowledgeServiceStatusUpdatesByVIN',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sequence_number', full_name='proto.AcknowledgeServiceStatusUpdatesByVIN.sequence_number', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=98,
)


_ACKNOWLEDGESERVICESTATUSUPDATE = _descriptor.Descriptor(
  name='AcknowledgeServiceStatusUpdate',
  full_name='proto.AcknowledgeServiceStatusUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sequence_number', full_name='proto.AcknowledgeServiceStatusUpdate.sequence_number', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=100,
  serialized_end=157,
)


_SERVICESTATUSUPDATESBYVIN_UPDATESENTRY = _descriptor.Descriptor(
  name='UpdatesEntry',
  full_name='proto.ServiceStatusUpdatesByVIN.UpdatesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='proto.ServiceStatusUpdatesByVIN.UpdatesEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='proto.ServiceStatusUpdatesByVIN.UpdatesEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=278,
  serialized_end=352,
)

_SERVICESTATUSUPDATESBYVIN = _descriptor.Descriptor(
  name='ServiceStatusUpdatesByVIN',
  full_name='proto.ServiceStatusUpdatesByVIN',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sequence_number', full_name='proto.ServiceStatusUpdatesByVIN.sequence_number', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='updates', full_name='proto.ServiceStatusUpdatesByVIN.updates', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_SERVICESTATUSUPDATESBYVIN_UPDATESENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=160,
  serialized_end=352,
)


_SERVICESTATUSUPDATE_UPDATESENTRY = _descriptor.Descriptor(
  name='UpdatesEntry',
  full_name='proto.ServiceStatusUpdate.UpdatesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='proto.ServiceStatusUpdate.UpdatesEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='proto.ServiceStatusUpdate.UpdatesEntry.value', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=545,
  serialized_end=613,
)

_SERVICESTATUSUPDATE = _descriptor.Descriptor(
  name='ServiceStatusUpdate',
  full_name='proto.ServiceStatusUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sequence_number', full_name='proto.ServiceStatusUpdate.sequence_number', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ciam_id', full_name='proto.ServiceStatusUpdate.ciam_id', index=1,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='vin', full_name='proto.ServiceStatusUpdate.vin', index=2,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='emit_timestamp', full_name='proto.ServiceStatusUpdate.emit_timestamp', index=3,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='emit_timestamp_in_ms', full_name='proto.ServiceStatusUpdate.emit_timestamp_in_ms', index=4,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='updates', full_name='proto.ServiceStatusUpdate.updates', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_SERVICESTATUSUPDATE_UPDATESENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=355,
  serialized_end=613,
)

_SERVICESTATUSUPDATESBYVIN_UPDATESENTRY.fields_by_name['value'].message_type = _SERVICESTATUSUPDATE
_SERVICESTATUSUPDATESBYVIN_UPDATESENTRY.containing_type = _SERVICESTATUSUPDATESBYVIN
_SERVICESTATUSUPDATESBYVIN.fields_by_name['updates'].message_type = _SERVICESTATUSUPDATESBYVIN_UPDATESENTRY
_SERVICESTATUSUPDATE_UPDATESENTRY.fields_by_name['value'].enum_type = _SERVICESTATUS
_SERVICESTATUSUPDATE_UPDATESENTRY.containing_type = _SERVICESTATUSUPDATE
_SERVICESTATUSUPDATE.fields_by_name['updates'].message_type = _SERVICESTATUSUPDATE_UPDATESENTRY
DESCRIPTOR.message_types_by_name['AcknowledgeServiceStatusUpdatesByVIN'] = _ACKNOWLEDGESERVICESTATUSUPDATESBYVIN
DESCRIPTOR.message_types_by_name['AcknowledgeServiceStatusUpdate'] = _ACKNOWLEDGESERVICESTATUSUPDATE
DESCRIPTOR.message_types_by_name['ServiceStatusUpdatesByVIN'] = _SERVICESTATUSUPDATESBYVIN
DESCRIPTOR.message_types_by_name['ServiceStatusUpdate'] = _SERVICESTATUSUPDATE
DESCRIPTOR.enum_types_by_name['ServiceStatus'] = _SERVICESTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AcknowledgeServiceStatusUpdatesByVIN = _reflection.GeneratedProtocolMessageType('AcknowledgeServiceStatusUpdatesByVIN', (_message.Message,), {
  'DESCRIPTOR' : _ACKNOWLEDGESERVICESTATUSUPDATESBYVIN,
  '__module__' : 'service_activation_pb2'
  # @@protoc_insertion_point(class_scope:proto.AcknowledgeServiceStatusUpdatesByVIN)
  })
_sym_db.RegisterMessage(AcknowledgeServiceStatusUpdatesByVIN)

AcknowledgeServiceStatusUpdate = _reflection.GeneratedProtocolMessageType('AcknowledgeServiceStatusUpdate', (_message.Message,), {
  'DESCRIPTOR' : _ACKNOWLEDGESERVICESTATUSUPDATE,
  '__module__' : 'service_activation_pb2'
  # @@protoc_insertion_point(class_scope:proto.AcknowledgeServiceStatusUpdate)
  })
_sym_db.RegisterMessage(AcknowledgeServiceStatusUpdate)

ServiceStatusUpdatesByVIN = _reflection.GeneratedProtocolMessageType('ServiceStatusUpdatesByVIN', (_message.Message,), {

  'UpdatesEntry' : _reflection.GeneratedProtocolMessageType('UpdatesEntry', (_message.Message,), {
    'DESCRIPTOR' : _SERVICESTATUSUPDATESBYVIN_UPDATESENTRY,
    '__module__' : 'service_activation_pb2'
    # @@protoc_insertion_point(class_scope:proto.ServiceStatusUpdatesByVIN.UpdatesEntry)
    })
  ,
  'DESCRIPTOR' : _SERVICESTATUSUPDATESBYVIN,
  '__module__' : 'service_activation_pb2'
  # @@protoc_insertion_point(class_scope:proto.ServiceStatusUpdatesByVIN)
  })
_sym_db.RegisterMessage(ServiceStatusUpdatesByVIN)
_sym_db.RegisterMessage(ServiceStatusUpdatesByVIN.UpdatesEntry)

ServiceStatusUpdate = _reflection.GeneratedProtocolMessageType('ServiceStatusUpdate', (_message.Message,), {

  'UpdatesEntry' : _reflection.GeneratedProtocolMessageType('UpdatesEntry', (_message.Message,), {
    'DESCRIPTOR' : _SERVICESTATUSUPDATE_UPDATESENTRY,
    '__module__' : 'service_activation_pb2'
    # @@protoc_insertion_point(class_scope:proto.ServiceStatusUpdate.UpdatesEntry)
    })
  ,
  'DESCRIPTOR' : _SERVICESTATUSUPDATE,
  '__module__' : 'service_activation_pb2'
  # @@protoc_insertion_point(class_scope:proto.ServiceStatusUpdate)
  })
_sym_db.RegisterMessage(ServiceStatusUpdate)
_sym_db.RegisterMessage(ServiceStatusUpdate.UpdatesEntry)


DESCRIPTOR._options = None
_SERVICESTATUSUPDATESBYVIN_UPDATESENTRY._options = None
_SERVICESTATUSUPDATE_UPDATESENTRY._options = None
# @@protoc_insertion_point(module_scope)