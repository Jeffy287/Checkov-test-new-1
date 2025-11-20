import re
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

# Regex: Matches ANY AWS ARN ending with :<number>
VERSION_PATTERN = re.compile(r'arn:aws:[^"\'\s]*:\d+(?=["\'\s]|$)')

class NoVersionPinnedARN(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ARNs do not contain version pinning"
        id = "CKV_AWS_CUSTOM_001"
        supported_resources = [
            "aws_batch_job_definition",
            "aws_lambda_function",
            "aws_ecs_task_definition",
            "aws_autoscaling_group",       # IAM roles and target group ARNs in Auto Scaling Groups
            "aws_launch_template",         # Instance profiles in Launch Templates
            "aws_lambda_layer_version",    # Layer versions in Lambda Layers
            "aws_sfn_state_machine",       # Roles and definitions in Step Functions State Machines
        ]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf, entity_type=None):
        """
        Scan the Terraform resource configuration for version-pinned ARNs.
        """
        keys_to_check = [
            "role",
            "execution_role_arn",
            "task_role_arn",
            "container_definitions",
            "layers",                    # Lambda functions and layers
            "service_linked_role_arn",
            "target_group_arns",
            "iam_instance_profile",
            "role_arn",                  # Step Functions
            "definition",                # Step Functions definition (can contain ARNs)
        ]
        for key in keys_to_check:
            if key in conf:
                if self._check_for_version_pinned_arn(conf[key]):
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def _check_for_version_pinned_arn(self, obj):
        """
        Recursively check strings, lists, and dictionaries for version-pinned ARNs.
        """
        if isinstance(obj, str):
            if VERSION_PATTERN.search(obj):
                return True
        elif isinstance(obj, list):
            for item in obj:
                if self._check_for_version_pinned_arn(item):
                    return True
        elif isinstance(obj, dict):
            for value in obj.values():
                if self._check_for_version_pinned_arn(value):
                    return True
        return False

# Instantiate the check
check = NoVersionPinnedARN()
