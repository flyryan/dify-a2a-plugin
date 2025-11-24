# Privacy Policy for A2A Client Plugin

**Last Updated:** November 23, 2025
**Plugin Version:** 0.1.0

## Overview

This privacy policy describes how the A2A Client plugin for Dify collects, uses, and protects your data. We are committed to transparency and protecting your privacy.

---

## Data Collection

This plugin collects and stores the following information to enable Agent-to-Agent (A2A) protocol communication:

### Types of Data Collected

#### 1. Agent Configuration Data

**Data Collected:**
- Agent base URLs (API endpoints)
- Agent authentication credentials (API keys, tokens, basic auth credentials)
- Agent names (identifiers you assign)
- Agent descriptions (optional text descriptions)

**Classification:**
- **Type A: Direct Identifiers** - API keys and authentication tokens
- **Type C: Combinable Data** - Base URLs, agent names, descriptions

**Purpose:**
- To authenticate with remote A2A-compatible agents
- To route communication requests to the correct agent endpoints
- To display available agents and their capabilities to users

#### 2. Message Content

**Data Handled (Not Stored by Plugin):**
- User instructions and messages sent to external agents
- Responses received from external agents
- Task IDs for asynchronous operations

**Important:** The plugin **does not store** message content or responses. All communication is pass-through only. Messages are:
- Temporarily held in memory during transmission
- Immediately discarded after delivery
- Never logged or persisted by the plugin

---

## How Data is Used

### Storage

All agent configuration data is stored securely within **Dify's credential management system**, which:
- Encrypts sensitive data at rest
- Uses secure access controls
- Is managed by the Dify platform (not this plugin)
- Follows Dify's security standards

The plugin itself **does not maintain any separate database or storage**.

### Usage

Agent configuration data is used exclusively to:

1. **Authenticate** - Provide credentials when connecting to remote agents
2. **Route requests** - Send user instructions to the correct agent endpoint
3. **Display information** - Show available agents and their descriptions in Dify workflows
4. **Enable protocol communication** - Format messages according to A2A protocol v0.3.0 specification

### Processing

- All data processing occurs within your Dify instance
- No data is sent to the plugin developer or any third parties except configured agent endpoints
- Communication uses standard HTTP/HTTPS protocols
- All JSON-RPC requests follow A2A protocol specification

---

## Third-Party Data Sharing

### Remote Agent Endpoints

**Data Shared with Third Parties:**

When you use this plugin, your user messages and instructions are sent to the **external agent endpoints that you explicitly configure**. This is the core functionality of the plugin.

**What is shared:**
- User instructions (the content you send to agents)
- Authentication credentials (to the specific agent you're calling)
- Message metadata (messageId, role, etc. as per A2A protocol)

**Important Notes:**

⚠️ **Each external agent operates independently** with its own privacy policy, data handling practices, and security measures.

⚠️ **The plugin developer (Ryan Duff) is not responsible for:**
- How external agents process or store data
- External agents' privacy practices
- Security of external agent endpoints
- Data retention policies of external agents

⚠️ **Your responsibility:**
- Review the privacy policy of each external agent before configuring it
- Ensure external agents meet your organization's security and privacy requirements
- Verify external agents are compliant with applicable regulations (GDPR, CCPA, etc.)

### No Other Third-Party Sharing

**This plugin does NOT share data with:**
- The plugin developer (Ryan Duff)
- Analytics services
- Advertising networks
- Data brokers
- Any other third parties

The only data transmission is to **agent endpoints that you explicitly configure**.

---

## Data Retention

### By This Plugin

- **Agent configuration:** Retained until you delete or reconfigure the plugin
- **Message content:** NOT stored - transmitted in real-time only
- **Logs:** Plugin uses Dify's standard logging (controlled by your Dify instance settings)

### By External Agents

- **Retention policies:** Determined by each external agent independently
- **User responsibility:** Review each agent's privacy policy for their data retention practices

---

## Data Security

### Security Measures

This plugin implements the following security practices:

1. **Credential Protection:**
   - Uses Dify's secure credential storage (encrypted at rest)
   - API keys stored as "secret-input" type (masked in UI)
   - No plaintext credential storage

2. **Transmission Security:**
   - Supports HTTPS for encrypted communication
   - Uses standard HTTP authentication headers (Bearer, Basic, API Key)
   - Follows JSON-RPC 2.0 protocol specification

3. **Access Control:**
   - Agent configurations only accessible to authorized Dify users
   - Credentials never exposed in tool outputs
   - Authentication required per Dify's access control policies

4. **No Code Execution:**
   - Plugin does not execute arbitrary code from external agents
   - All responses are treated as data only
   - No eval() or dynamic code execution

### User Responsibilities

For maximum security, you should:

✅ Use HTTPS endpoints for all agent base URLs
✅ Rotate API keys regularly
✅ Use separate credentials for each agent (don't reuse keys)
✅ Review external agent security certifications
✅ Monitor agent access logs in Dify
✅ Immediately revoke credentials if compromised
✅ Only configure agents from trusted sources

---

## User Rights

Depending on your jurisdiction (GDPR, CCPA, etc.), you may have rights regarding your data:

### Your Rights

- **Access:** You can view all agent configurations in the plugin settings
- **Modification:** You can update agent configurations at any time
- **Deletion:** You can delete agent configurations or uninstall the plugin entirely
- **Portability:** Agent configurations are stored in Dify's database (exportable via Dify's tools)

### Exercising Rights

To exercise these rights:
1. Access plugin configuration in Dify
2. Modify or delete agent settings as needed
3. For Dify platform data: Contact your Dify instance administrator
4. For questions about this plugin: Contact ry@nduff.com

---

## Compliance

### Regulations

This plugin is designed to be compatible with:
- **GDPR** (General Data Protection Regulation)
- **CCPA** (California Consumer Privacy Act)
- **SOC 2** compliance frameworks
- Industry-standard security practices

**Note:** Compliance also depends on:
- Your Dify instance configuration
- External agents you choose to use
- Your organization's data handling policies

### A2A Protocol Compliance

- Implements A2A Protocol v0.3.0 specification
- Follows JSON-RPC 2.0 standards
- Uses standard HTTP authentication methods
- Supports agent discovery via agent cards

---

## Children's Privacy

This plugin is not directed at children under the age of 13 (or applicable age in your jurisdiction). We do not knowingly collect personal information from children.

If you believe a child has provided data through this plugin, please contact us immediately at ry@nduff.com.

---

## Changes to This Privacy Policy

We may update this privacy policy from time to time. Changes will be reflected in:
- The "Last Updated" date at the top of this document
- Plugin version number
- Dify marketplace plugin listing

**How you'll be notified:**
- Updated PRIVACY.md file in the repository
- Plugin version updates in Dify marketplace
- Major changes will be communicated via plugin release notes

**Your responsibility:** Review this privacy policy periodically for changes.

---

## International Data Transfers

### Data Location

- Agent configuration data is stored in your Dify instance (location depends on your Dify deployment)
- Messages are transmitted to external agent endpoints (location varies by agent)

### Cross-Border Transfers

If your external agents are located in different countries:
- Data will cross international borders during transmission
- Encryption (HTTPS) should be used for all transfers
- Verify external agents comply with applicable international data protection laws

---

## Contact Information

### For Privacy Questions

If you have questions, concerns, or requests regarding this privacy policy or data handling:

**Plugin Developer:**
- **Name:** Ryan Duff
- **Email:** ry@nduff.com
- **GitHub:** https://github.com/flyryan
- **Issues:** https://github.com/flyryan/dify-a2a-plugin/issues

**Response Time:** We aim to respond to privacy inquiries within 5 business days.

### For Dify Platform Issues

For questions about Dify's data handling practices:
- Contact your Dify instance administrator
- See Dify's privacy policy: https://dify.ai/privacy

### For External Agent Issues

For privacy questions about specific external agents:
- Review each agent's privacy policy
- Contact the agent provider directly
- We cannot answer questions about third-party agent data practices

---

## Disclaimer

This plugin is provided "as is" without warranties of any kind. The plugin developer is not responsible for:

- Data handling practices of external agents
- Security incidents at external agent endpoints
- Compliance violations by third-party agents
- Data breaches at external agent services
- Loss or unauthorized access to agent credentials

**Users assume all risk** associated with configuring and using external agent endpoints.

---

## Acknowledgments

This privacy policy follows the guidelines provided by:
- Dify Plugin Developer Agreement
- Dify Privacy Protection Guidelines
- A2A Protocol Privacy Recommendations

---

**By using this plugin, you acknowledge that you have read and understood this privacy policy and agree to its terms.**

For the most up-to-date version of this policy, visit:
https://github.com/flyryan/dify-a2a-plugin/blob/main/PRIVACY.md
