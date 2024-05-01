import { images } from "../_images";

export interface Attack {
  id: number;
  name: string;
  description: string;
  platform: string;
  isDisabled?: boolean;
  // Endpoints
  createEndpoint?: string;
  statusEndpoint?: string;
  attackEndpoint?: string;
  startDestroyEndpoint?: string;
  completeDestroyEndpoint?: string;
  finalLogsEndpoint?: string;
}

interface AttackPipelineStep {
  title: string;
  imageSrc?: any;
  description: {
    title: string;
    content: string;
  };
}

export interface AttackPipeline {
  [attack_id: number]: AttackPipelineStep[];
}

export const STATUS_POOLING_INTERVAL = 2000;

export const ATTACK_LIST: Attack[] = [
  {
    id: 1,
    name: "IAM Role Hijack and SSM Parameter Store Data Breach",
    platform: "AWS",
    description:
      "In this attack scenario, an attacker gains initial access using stolen AWS credentials and undertakes reconnaissance to pinpoint the lambdaManager role for IAM-based privilege escalation. To avoid detection, they employ AWS Lambda to alter IAM policies and run a Lambda function, thus amplifying their access privileges. The attacker generates new AWS console login credentials with heightened permissions to secure ongoing access. The attack culminates with the exfiltration of sensitive information from the AWS SSM Parameter Store, ensuring the attacker retains access, even if the initially compromised credentials are detected and neutralized.",
    // Endpoints
    createEndpoint: "lambda_privesc_create",
    statusEndpoint: "lambda_privesc_status",
    attackEndpoint: "lambda_privesc_attack",
    startDestroyEndpoint: "lambda_privesc_start_destroy",
    completeDestroyEndpoint: "lambda_privesc_complete_destroy",
  },
  {
    id: 2,
    name: "IAM Policy Rollback to S3 Ransomware via KMS key",
    description:
      "In this scenario, an attacker with initial, limited access under the IAM user exploits the SetDefaultPolicyVersion permission to escalate privileges by restoring an old policy version that grants full admin rights. With elevated privileges, the attacker creates a new IAM user with S3 admin permissions, then enumerates and targets S3 buckets. The final step involves encrypting objects in the S3 buckets with an attacker-controlled KMS key and deleting the original objects, compromising data integrity and availability and potentially causing a significant impact on the organization's operations. This sophisticated attack chain systematically exploits cloud configurations for privilege escalation and executing a malicious agenda.",
    platform: "AWS",
    createEndpoint: "policy_ransom_exploit_create",
    statusEndpoint: "policy_ransom_exploit_status",
    attackEndpoint: "policy_ransom_exploit_attack",
    startDestroyEndpoint: "policy_ransom_exploit_start_destroy",
    completeDestroyEndpoint: "policy_ransom_exploit_complete_destroy",
  },
  {
    id: 3,
    name: "EC2 Credential Compromise and RDS Snapshot Exfiltration",
    description:
      "In this attack scenario, the attacker gains initial entry with compromised EC2 credentials, then leverages the EC2 instance profile to extend their access across AWS resources. Upon discovering they have full RDS permissions, the attacker proceeds to exfiltrate data by sharing an RDS snapshot with an external account, effectively utilizing AWS features to extract sensitive information.",
    platform: "AWS",
    createEndpoint: "snapshot_exfil_create",
    statusEndpoint: "snapshot_exfil_status",
    attackEndpoint: "snapshot_exfil_attack",
    startDestroyEndpoint: "snapshot_exfil_start_destroy",
    completeDestroyEndpoint: "snapshot_exfil_complete_destroy",
  },
];

export const CREATE_INFRASTRUCTURE_PIPELINE: AttackPipeline = {
  1: [
    {
      title: "Creating IAM User",
      imageSrc: images.emptyImage,
      description: {
        title: "sean@zti.com",
        content:
          "An IAM user has the necessary permissions to assume more provileged IAM roles that grant extensive access to an AWS account.",
      },
    },
    {
      title: "Creating IAM Role",
      imageSrc: images.emptyImage,
      description: {
        title: "lambda-manager-role",
        content: "An IAM role with elevated permissions for lambda access and pass role permissions.",
      },
    },
    {
      title: "Creating IAM Service Role",
      imageSrc: images.emptyImage,
      description: {
        title: "lambdaDebug-serviceRole",
        content: "An IAM role with full administrator privileges, assumable only by AWS Lambda",
      },
    },
    {
      title: "Creating 10 SSM Parameter Store values",
      imageSrc: images.emptyImage,
      description: {
        title: "/zerotoimpact",
        content: "The AWS SSM Parameter Store will hold company sensitive data",
      },
    },
  ],
  2: [
    {
      title: "Creating IAM User and IAM policies",
      imageSrc: images.emptyImage,
      description: {
        title: "john@zti.com",
        content:
          "Creating an IAM user with several IAM policies attached, one of which grants full administrator permissions. This specific policy will be the target for rollback and exploitation by the attacker.",
      },
    },
    {
      title: "Creating S3 bucket with files",
      imageSrc: images.emptyImage,
      description: {
        title: "zti-bucket-to-ransomware",
        content:
          "Creating an S3 bucket filled with files that the attacker plans to encrypt with a KMS key under their control, subjecting it to a ransomware attack.",
      },
    }
  ],
  3: [
    {
      title: "Creating EC2 Instance Profile with RDS permissions",
      imageSrc: images.emptyImage,
      description: {
        title: "EC2RDSFullAccessRole",
        content:
          "Creating an IAM role with RDS permissions and linking it to an EC2 instance profile to grant the EC2 instance access to RDS resources.",
      },
    },
    {
      title: "Launching EC2 Instance Profile with RDS permissions",
      imageSrc: images.emptyImage,
      description: {
        title: "EC2 Instance",
        content:
          "Launching an EC2 instance that will later have its instance profile compromised by the attacker.",
      },
    },
    {
      title: "Launching RDS instance",
      imageSrc: images.emptyImage,
      description: {
        title: "zti-db-instance-id",
        content:
          "Launching an RDS instance from which a snapshot will be created.",
      },
    },
    {
      title: "Creating RDS snapshot",
      imageSrc: images.emptyImage,
      description: {
        title: "zti-db-snapshot-id",
        content:
          "Creating an RDS snapshot that will be shared with an external account under the attacker's control.",
      },
    },
  ]
};

export const ATTACK_PIPELINE: AttackPipeline = {
  1: [
    {
      title: "Initial Access",
      imageSrc: images.emptyImage,
      description: {
        title: "Valid Accounts (T1078)",
        content:
          "The attacker initially uses compromised AWS credentials to gain access to the environment. This technique is utilized when attackers leverage legitimate but stolen credentials to gain initial foothold in the cloud environment.",
      },
    },
    {
      title: "Discovery (step 1)",
      imageSrc: images.emptyImage,
      description: {
        title: "Permission Groups Discovery (T1069)",
        content:
          "The attacker analyzes their own privileges and lists available IAM roles, identifying lambdaManager and debug roles. This step involves understanding what permissions and roles are available to them within the compromised environment.",
      },
    },
    {
      title: "Discovery (step 2)",
      imageSrc: images.emptyImage,
      description: {
        title: "Additive Permissions (T1098)",
        content:
          "The attacker attempts to escalate privileges by trying to assume more powerful roles. Specifically, they target the lambdaManager role for its permissions that could be exploited to escalate privileges further.",
      },
    },
    {
      title: "Defense Evasion",
      imageSrc: images.emptyImage,
      description: {
        title: "Modify Cloud Compute Infrastructure (T1578)",
        content:
          "By creating a Lambda function with the intention to modify IAM policies, the attacker aims to evade defenses. The use of a legitimate service (AWS Lambda) to perform malicious actions helps in staying under the radar.",
      },
    },
    {
      title: "Execution",
      imageSrc: images.emptyImage,
      description: {
        title: "Serverless Execution (T1530)",
        content:
          "The attacker deploys and executes a Lambda function to perform the intended malicious actions. This demonstrates the execution of code in a serverless environment to achieve their objectives.",
      },
    },
    {
      title: "Persistence",
      imageSrc: images.emptyImage,
      description: {
        title: "Account Manipulation (T1098)",
        content:
          "Creating new AWS console login credentials for themselves, with elevated permissions, ensures that the attacker maintains access to the environment even if the original compromised credentials are discovered and revoked",
      },
    },
    {
      title: "Exfiltration",
      imageSrc: images.emptyImage,
      description: {
        title: "Data from Cloud Storage Object (T1530)",
        content:
          "The attacker leverages their elevated permissions to access and exfiltrate sensitive data stored in AWS SSM Parameter Store, extracting valuable secrets and configurations for further exploitation or leverage.",
      },
    },
  ],
  2: [
    {
      title: "Discovery",
      imageSrc: images.emptyImage,
      description: {
        title: "Cloud Service Discovery (T1526)",
        content:
          "The attacker conducts reconnaissance to discover historical IAM permission policies.",
      }
    },
    {
      title: "Privilege Escalation",
      imageSrc: images.emptyImage,
      description: {
        title: "Modify Cloud Compute Infrastructure (T1578)",
        content:
          "The attacker escalates privileges by rolling back to a historical IAM policy that grants administrator permissions.",
      }
    },
    {
      title: "Impact",
      imageSrc: images.emptyImage,
      description: {
        title: "Data Encrypted for Impact (T1486) & Data Destruction (T1485)",
        content:
          "This will take while! The attacker encrypts data in S3 buckets, impacting its availability and integrity. Deleting the original objects from the source bucket after moving them ensures the data cannot be easily recovered.",
      }
    },
    {
      title: "Exfiltration",
      imageSrc: images.emptyImage,
      description: {
        title: "Transfer Data to Cloud Account (T1537)",
        content:
          "The attacker moves encrypted objects to a different S3 bucket controlled by them, effectively exfiltrating the data.",
      }
    },
  ],
  3: [
    {
      title: "Credential Access",
      imageSrc: images.emptyImage,
      description: {
        title: "AWS IAM Role to Instance Profile Addition (T1098)",
        content:
          "The attacker gains initial access with compromised EC2 instance credentials, exploiting legitimate but unauthorized access to misuse the EC2 instance profile credentials for broader AWS resource access, representing a strategic exploitation of roles and credentials within the AWS environment.",
      }
    },
    {
      title: "Discovery",
      imageSrc: images.emptyImage,
      description: {
        title: "Cloud Service Discovery (T1526)",
        content:
          "The attacker conducts reconnaissance within the compromised EC2 instance to identify full RDS permissions, uncovering the extent of their access within the cloud environment.",
      }
    },
    {
      title: "Exfiltration",
      imageSrc: images.emptyImage,
      description: {
        title: "Data from Cloud Storage Object (T1530)",
        content:
          "The attacker exfiltrates data by sharing an RDS snapshot with an external, attacker-controlled AWS account. This process utilizes AWS mechanisms for data movement, specifically targeting the database service for sensitive information extraction.",
      }
    },
  ]
};
