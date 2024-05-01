<h1 align="center">
    <img src="https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png" height="96">
    <br>
    ZeroToImpact
    <br>
</h1>
<h4 align="center">The <b>ZeroToImpact</b> Project: Simulate, understand, and mitigate cybersecurity threats from inception to impact.
</h4>

![zti](https://github.com/agroyz/zerotoimpact/assets/140458593/f66a6390-8ce1-4bce-9e56-e2f3f4d906db)

<p align="center">
An interactive, web-based educational platform meticulously crafted to emulate cyberattacks across cloud environments, providing a comprehensive understanding of attack methodologies and defense strategies. Featuring a seamless one-click attack initiation, our dedicated application delivers a user-friendly, hands-on learning experience tailored to attack emulation, empowering users to explore, simulate, and analyze cyber threats from inception to resolution.
</p>


## Setup Instructions
## Setup Instructions
**1. Install Node.js, Python, and AWS CLI:** If not already installed, download and install [Node.js](https://nodejs.org/en/download), [Python](https://www.python.org/downloads/), [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

**2. Create a Python Virtual Environment:**

```powershell
python3 -m venv .venv
```
**3. Activate the Virtual Environment:**

```bash
.venv/Scripts/activate
```
**4. Install Dependencies:**

```bash
npm install
```
**5. Set Enviroment Variable:**

***Windown***
```powershell
$env:AWS_DEFAULT_PROFILE="your_aws_profile_to_use"
```
***Linux***
```bash
export AWS_DEFAULT_PROFILE="your_aws_profile_to_use"
```

**6. Run the Development Server:**

```bash
npm run dev
```

**6. Access the Application:** Open http://localhost:3000 in your browser to access the application.

**Note**: The Flask server will be running on http://127.0.0.1:5328 – feel free to change the port in ***package.json'*** (you'll also need to update it in ***'next.config.js'***).




## Usage
- **Explore Attack Scenarios:** Use the interactive interface to explore different attack scenarios categorized by MITRE ATT&CK tactics.

- **Analyze Attack Paths:** Analyze the progression of attacks from initial compromise to lateral movement and exfiltration.

- **Mitigate Attacks:** Implement mitigation strategies based on the insights gained from analyzing attack paths.

