# -*- coding: utf-8 -*-

"""Policy Engine For cdsoss"""

import copy
import os.path

from cdsoss.common import cfg

from cdsoss.common import exception
from cdsoss.common import jsonutils
import cdsoss.common.log as logging
from cdsoss.common import policy

LOG = logging.getLogger(__name__)

policy_opts = [
    cfg.StrOpt('policy_file', default='policy.json',
               help=_('The location of the policy file.')),
    cfg.StrOpt('policy_default_rule', default='default',
               help=_('The default policy to use.')),
]

CONF = cfg.CONF
CONF.register_opts(policy_opts)


DEFAULT_RULES = {
    'context_is_admin': policy.RoleCheck('role', 'admin'),
    'default': policy.TrueCheck()
}


class Enforcer(object):
    """Responsible for loading and enforcing rules"""

    def __init__(self):
        self.default_rule = CONF.policy_default_rule
        self.policy_path = self._find_policy_file()
        self.policy_file_mtime = None
        self.policy_file_contents = None
        self.load_rules()

    def set_rules(self, rules):
        """Create a new Rules object based on the provided dict of rules"""
        rules_obj = policy.Rules(rules, self.default_rule)
        policy.set_rules(rules_obj)

    def add_rules(self, rules):
        """Add new rules to the Rules object"""
        if policy._rules:
            rules_obj = policy.Rules(rules)
            policy._rules.update(rules_obj)
        else:
            self.set_rules(rules)

    def load_rules(self):
        """Set the rules found in the json file on disk"""
        if self.policy_path:
            rules = self._read_policy_file()
            rule_type = ""
        else:
            rules = DEFAULT_RULES
            rule_type = "default "

        text_rules = dict((k, str(v)) for k, v in rules.items())
        msg = (_('Loaded %(rule_type)spolicy rules: %(text_rules)s') %
               {'rule_type': rule_type, 'text_rules': text_rules})
        LOG.debug(msg)

        self.set_rules(rules)

    @staticmethod
    def _find_policy_file():
        """Locate the policy json data file"""
        policy_file = CONF.find_file(CONF.policy_file)
        if policy_file:
            return policy_file
        else:
            LOG.warn(_('Unable to find policy file'))
            return None

    def _read_policy_file(self):
        """Read contents of the policy file

        This re-caches policy data if the file has been changed.
        """
        mtime = os.path.getmtime(self.policy_path)
        if not self.policy_file_contents or mtime != self.policy_file_mtime:
            LOG.debug(_("Loading policy from %s") % self.policy_path)
            with open(self.policy_path) as fap:
                raw_contents = fap.read()
                rules_dict = jsonutils.loads(raw_contents)
                self.policy_file_contents = dict(
                    (k, policy.parse_rule(v))
                    for k, v in rules_dict.items())
            self.policy_file_mtime = mtime
        return self.policy_file_contents

    def _check(self, context, rule, target, *args, **kwargs):
        """Verifies that the action is valid on the target in this context.

           :param context: request context
           :param rule: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :raises: `cdsoss.common.exception.Forbidden`
           :returns: A non-False value if access is allowed.
        """
        credentials = {
            'roles': context.roles,
            'user': context.user,
            'tenant': context.tenant,
        }

        return policy.check(rule, target, credentials, *args, **kwargs)

    def enforce(self, context, action, target):
        """Verifies that the action is valid on the target in this context.

           :param context: request context
           :param action: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :raises: `cdsoss.common.exception.Forbidden`
           :returns: A non-False value if access is allowed.
        """
        return self._check(context, action, target,
                           exception.Forbidden, action=action)

    def check(self, context, action, target):
        """Verifies that the action is valid on the target in this context.

           :param context: Glance request context
           :param action: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :returns: A non-False value if access is allowed.
        """
        return self._check(context, action, target)

    def check_is_admin(self, context):
        """Check if the given context is associated with an admin role,
           as defined via the 'context_is_admin' RBAC rule.

           :param context: Glance request context
           :returns: A non-False value if context role is admin.
        """
        target = context.to_dict()
        return self.check(context, 'context_is_admin', target)

