<h1 align="center">
    ZeroToImpact
</h1>
<h4 align="center">The <b>ZeroToImpact</b> Project: Simulate, understand, and mitigate cybersecurity threats from inception to impact.
</h4>

![zti](./images/zti.gif)

<p align="center">
An interactive, web-based educational platform meticulously crafted to emulate cyberattacks across cloud environments, providing a comprehensive understanding of attack methodologies and defense strategies. Featuring a seamless one-click attack initiation, our dedicated application delivers a user-friendly, hands-on learning experience tailored to attack emulation, empowering users to explore, simulate, and analyze cyber threats from inception to resolution.
</p>


## Setup Instructions
**1. Install Node.js, Python, and AWS CLI:** If not already installed, download and install [Node.js](https://nodejs.org/en/download), [Python](https://www.python.org/downloads/), [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

**2. Navigate to the application directory:**
```powershell
cd .\zerotoimpact\
```

**3. Create a Python Virtual Environment:**

```powershell
python3 -m venv .venv
```
**4. Activate the Virtual Environment:**

***Windows***
```powershell
.venv/Scripts/activate
```
***Linux***
```bash
source .venv/bin/activate
```

**5. Install Dependencies:**

```bash
npm install
```
**6. Set Enviroment Variable:**

***AWS Profile Permissions***
The AWS profile requires AdministratorAccess permission to deploy the vulnerable infrastructure. However, the profile will not be used to execute the attacks 

***AWS Region Support***
This application currently supports only the us-east-1 AWS region. Please ensure that your AWS environment is configured to use us-east-1 by setting the AWS_DEFAULT_REGION environment variable accordingly. Attempting to use the application in any other region may result in errors during resource creation or operations.

***Windows***
```powershell
$env:AWS_DEFAULT_PROFILE="your_aws_profile_to_use"
$env:AWS_DEFAULT_REGION="us-east-1"
```
***Linux***
```bash
export AWS_DEFAULT_PROFILE="your_aws_profile_to_use"
export AWS_DEFAULT_REGION="us-east-1"
```

**7. Run the Development Server:**

```bash
npm run dev
```

**8. Access the Application:** Open http://localhost:3000 in your browser to access the application.

**Note**: The Flask server will be running on http://127.0.0.1:5328 – feel free to change the port in ***package.json'*** (you'll also need to update it in ***'next.config.js'***).


## Usage
- **Explore Attack Scenarios:** Use the interactive interface to explore different attack scenarios categorized by MITRE ATT&CK tactics.

- **Analyze Attack Paths:** Analyze the progression of attacks from initial compromise to lateral movement and exfiltration.

- **Mitigate Attacks:** Implement mitigation strategies based on the insights gained from analyzing attack paths.


## Troubleshooting

If an error occurs, the application's **Activity Log** section will notify you and may suggest destroying resources created during the attack. It's crucial to remove these resources to avoid unnecessary charges and because you must destroy the resources before rerunning the attack with the same username.

**Important:** Before destroying resources, navigate to the application directory and retrieve the logs from the current application run. Destroying resources through the application also wipes out these logs.

Logs can be found in the `api/{attack_emulation}/instances` directory as a JSON file. 

For example, logs generated during the 'IAM Policy Rollback to S3 Ransomware via KMS key' attack emulation are located in the `api/policy_ransom_exploit/instances` directory.


## Acknowledgments

Maintainer: [@alexgroyz](https://twitter.com/nightmareJs)

## Contact
If you found this tool useful, want to share an interesting use-case, bring issues to attention, whatever the reason - share them. You can email at: agroyz@vectra.ai.

