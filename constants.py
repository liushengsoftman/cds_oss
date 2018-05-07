# -*- coding: utf-8 -*-


CPSWD = 'CDSP@ssw0rd'

NETWORK_TYPE_PRIVATE = 'private'
NETWORK_TYPE_PUBLIC = 'public'
NETWORK_TYPE_CTL_PRIVATE = 'ctl_private'
NETWORK_TYPE_GPN = 'gpn'

VM_ACTIVE_STATUS = 'active'
VM_ERROR_STATUS = 'error'
VM_SHUTDOWN_STATUS = 'shutdown'
VM_UPDATING_STATUS = 'updating'
VM_REBOOTING_STATUS = 'rebooting'

VOLUME_AVAILABLE_STATUS = 'available'
VOLUME_IN_USE_STATUS = 'in-use'
VOLUME_ERROR_STATUS = 'error'
VOLUME_CREATING_STATUS = 'creating'
VOLUME_DELETE_ACTION = 'delete'
VOLUME_CREATE_ACTION = 'create'

TASK_PROCESSING_STATUS = 'processing'
TASK_ERROR_STATUS = 'error'
TASK_SUCCESS_STATUS = 'success'

TASK_CREATE_VM_TYPE = 'create_vm'
TASK_DELETE_VM_TYPE = 'delete_vm'
TASK_UPDATE_VM_TYPE = 'update_vm'
TASK_CREATE_NETWORK_TYPE = 'create_network'
TASK_DELETE_NETWORK_TYPE = 'delete_network'

TASK_ERROR_CODE_10000 = {
    'code': 'ER10000',
    'msg': 'Input args is error.'
    }

TASK_ERROR_CODE_10001 = {
    'code': 'ER10001',
    'msg': 'Get auth failed.'
    }

TASK_ERROR_CODE_10010 = {
    'code': 'ER10010',
    'msg': 'Create network failed.'
    }

TASK_ERROR_CODE_10011 = {
    'code': 'ER10011',
    'msg': 'Create subnet failed.'
    }

TASK_ERROR_CODE_10012 = {
    'code': 'ER10012',
    'msg': 'Create router failed.'
    }

TASK_ERROR_CODE_10013 = {
    'code': 'ER10013',
    'msg': 'Set router gateway failed.'
    }

TASK_ERROR_CODE_10014 = {
    'code': 'ER10014',
    'msg': 'Add router interface failed.'
    }

TASK_ERROR_CODE_10015 = {
    'code': 'ER10015',
    'msg': 'Create gpn port failed.'
    }

TASK_ERROR_CODE_10016 = {
    'code': 'ER10016',
    'msg': 'Delete router interface failed.'
    }

TASK_ERROR_CODE_10017 = {
    'code': 'ER10017',
    'msg': 'Delete router failed.'
    }

TASK_ERROR_CODE_10018 = {
    'code': 'ER10018',
    'msg': 'Delete network failed.'
    }

TASK_ERROR_CODE_10100 = {
    'code': 'ER10100',
    'msg': 'Prepare vm flavor or image failed.'
    }

TASK_ERROR_CODE_10101 = {
    'code': 'ER10101',
    'msg': 'Create vm failed.'
    }

TASK_ERROR_CODE_10102 = {
    'code': 'ER10102',
    'msg': 'Create vm expired.'
    }

TASK_ERROR_CODE_10103 = {
    'code': 'ER10103',
    'msg': 'The vm status be error.'
    }

TASK_ERROR_CODE_10104 = {
    'code': 'ER10104',
    'msg': 'Attach volume error.'
    }

TASK_ERROR_CODE_10105 = {
    'code': 'ER10105',
    'msg': 'Resize vm expired.'
    }

TASK_ERROR_CODE_10106 = {
    'code': 'ER10106',
    'msg': 'Get vm port failed.'
    }

TASK_ERROR_CODE_10107 = {
    'code': 'ER10107',
    'msg': 'Delete vm failed.'
    }

TASK_ERROR_CODE_10108 = {
    'code': 'ER10108',
    'msg': 'Resize vm failed.'
    }

TASK_ERROR_CODE_10200 = {
    'code': 'ER10200',
    'msg': 'Create volume failed.'
    }

TASK_ERROR_CODE_10201 = {
    'code': 'ER10201',
    'msg': 'Create volume error.'
    }

TASK_ERROR_CODE_10202 = {
    'code': 'ER10202',
    'msg': 'Delete volume failed.'
    }