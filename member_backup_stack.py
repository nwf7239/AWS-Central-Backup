from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_backup as backup,
    CfnOutput
)
from constructs import Construct

class MemberBackupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, central_account_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Parameters
        central_role_arn = f"arn:aws:iam::{central_account_id}:role/CrossAccountBackupRole"
        
        # Create IAM role for backup service in member account
        backup_role = iam.Role(
            self, "MemberBackupRole",
            assumed_by=iam.ServicePrincipal("backup.amazonaws.com"),
            description="Role for AWS Backup to perform cross-account operations",
            role_name="MemberBackupRole"
        )
        
        # Add permissions to assume the central role
        backup_role.add_to_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"],
            resources=[central_role_arn]
        ))
        
        # Create backup plan in member account (optional)
        backup_plan = backup.BackupPlan(
            self, "MemberBackupPlan",
            backup_plan_name="MemberBackupPlan"
        )
        
        # Add rules to the plan
        backup_plan.add_rule(backup.BackupPlanRule(
            enable_continuous_backup=True,
            delete_after=Duration.days(30),
            rule_name="DailyBackups"
        )
        
        CfnOutput(self, "MemberBackupRoleArn", value=backup_role.role_arn)
