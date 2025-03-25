from aws_cdk import (
    Stack,
    aws_backup as backup,
    aws_iam as iam,
    aws_organizations as orgs,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct

class CentralBackupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Parameters
        backup_vault_name = "CentralBackupVault"
        member_ou_ids = ["ou-xxxx-xxxxxxx"]  # Replace with your OU IDs
        
        # Create the central backup vault
        backup_vault = backup.BackupVault(
            self, "CentralBackupVault",
            backup_vault_name=backup_vault_name,
            removal_policy=RemovalPolicy.RETAIN,
            encryption_key=None  # Add KMS key if needed
        )
        
        # Create IAM role for member accounts to use
        backup_role = iam.Role(
            self, "CrossAccountBackupRole",
            assumed_by=iam.CompositePrincipal(
                iam.AccountPrincipal(self.account),
                iam.ServicePrincipal("backup.amazonaws.com")
            ),
            description="Role for member accounts to send backups to central vault",
            role_name="CrossAccountBackupRole"
        )
        
        # Add permissions to the role
        backup_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "backup:CopyIntoBackupVault",
                "backup:StartCopyJob",
                "backup:DescribeCopyJob",
                "backup:ListCopyJobs"
            ],
            resources=["*"]
        ))
        
        # Allow member accounts to assume the role
        for ou_id in member_ou_ids:
            backup_role.assume_role_policy.add_statements(
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    principals=[iam.ArnPrincipal(f"arn:aws:iam::{self.account}:root")],
                    conditions={
                        "StringEquals": {
                            "aws:PrincipalOrgID": [ou_id]
                        }
                    }
                )
            )
        
        # Outputs
        CfnOutput(self, "BackupVaultArn", value=backup_vault.backup_vault_arn)
        CfnOutput(self, "BackupRoleArn", value=backup_role.role_arn)
