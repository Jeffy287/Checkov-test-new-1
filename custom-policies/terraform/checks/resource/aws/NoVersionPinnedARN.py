import re
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

# Regex to match ARNs with version pinning (numbers at the end after colon)
VERSION_PATTERN = re.compile(r'arn:aws:[^:]+:[^:]*:[^:]*:[^:]+:\d+$')

class NoVersionPinnedARN(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ARNs do not contain version pinning"
        id = "CKV_AWS_CUSTOM_001"
        supported_resources = [
            "aws_batch_job_definition",
            "aws_lambda_function",
            "aws_ecs_task_definition",
            "aws_autoscaling_group",       # Checks IAM roles and target group ARNs in Auto Scaling Groups
            "aws_launch_template",         # Checks instance profiles in Launch Templates
            "aws_lambda_layer_version",    # Checks layer versions in Lambda Layers
            "aws_sfn_state_machine",       # Checks roles and definitions in Step Functions State Machines
        ]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf, entity_type=None):
        """
        Scan the Terraform resource configuration for version-pinned ARNs.
        """
        # List of attribute keys likely to contain ARNs in the supported resources
        keys_to_check = [
            "role",
            "execution_role_arn",
            "task_role_arn",
            "container_definitions",
            "layers",                    # Lambda function can have layers with version
            "service_linked_role_arn",   # Used in Auto Scaling Groups for roles
            "target_group_arns",         # Used in Auto Scaling Groups for referenced resources
            "iam_instance_profile",      # Used in Launch Templates for profiles
            "role_arn",                  # Used in Step Functions for role assignment
            "definition",                # Step Functions definition, may reference versioned functions
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
