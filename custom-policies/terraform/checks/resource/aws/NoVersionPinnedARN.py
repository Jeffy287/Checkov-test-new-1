import re
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

# Regex: match any AWS ARN ending with :<number> (version pin)
VERSION_PATTERN = re.compile(r'arn:aws:[^"\'\s]*:\d+(?=["\'\s]|$)')

class NoVersionPinnedARN(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ARNs do not contain version pinning"
        id = "CKV_AWS_CUSTOM_001"
        supported_resources = [
            "aws_batch_job_definition",
            "aws_lambda_function",
            "aws_ecs_task_definition",
            "aws_autoscaling_group",
            "aws_launch_template",
            "aws_lambda_layer_version",
            "aws_sfn_state_machine",
        ]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf, entity_type=None):
        """
        Scan the resource configuration for any string/list/dict containing version-pinned ARNs.
        """
        # Keys that often contain ARNs
        keys_to_check = [
            "role",
            "execution_role_arn",
            "task_role_arn",
            "container_definitions",
            "layers",
            "service_linked_role_arn",
            "target_group_arns",
            "iam_instance_profile",
            "role_arn",
            "definition",
        ]

        for key in keys_to_check:
            if key in conf:
                if self._contains_version_pinned_arn(conf[key]):
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def _contains_version_pinned_arn(self, obj):
        """
        Recursively check strings, lists, dicts for version-pinned ARNs.
        """
        if isinstance(obj, str):
            if VERSION_PATTERN.search(obj):
                return True
        elif isinstance(obj, list):
            for item in obj:
                if self._contains_version_pinned_arn(item):
                    return True
        elif isinstance(obj, dict):
            for value in obj.values():
                if self._contains_version_pinned_arn(value):
                    return True
        return False

# Instantiate the check
check = NoVersionPinnedARN()
