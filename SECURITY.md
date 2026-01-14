# Security Update - January 2026

## Summary
Updated all vulnerable dependencies to their patched versions to address critical security vulnerabilities.

## Vulnerabilities Fixed

### LangChain Community (0.0.13 → 0.3.27)
1. **XXE (XML External Entity) Attacks**
   - Severity: High
   - Affected: < 0.3.27
   - Fixed in: 0.3.27

2. **SSRF in RequestsToolkit**
   - Severity: High
   - Affected: < 0.0.28
   - Fixed in: 0.3.27

3. **Pickle Deserialization of Untrusted Data**
   - Severity: Critical
   - Affected: < 0.2.4
   - Fixed in: 0.3.27

### Llama Index Core (0.9.48 → 0.13.0)
1. **Insecure Temporary File Handling**
   - Severity: Medium
   - Affected: < 0.13.0
   - Fixed in: 0.13.0

2. **DOS in JSONReader**
   - Severity: Medium
   - Affected: < 0.12.38
   - Fixed in: 0.13.0

3. **Arbitrary Code Execution via exec call**
   - Severity: Critical
   - Affected: < 0.10.38
   - Fixed in: 0.13.0

4. **Command Injection**
   - Severity: Critical
   - Affected: < 0.10.24
   - Fixed in: 0.13.0

5. **Prompt Injection leading to Code Execution**
   - Severity: Critical
   - Affected: < 0.10.24
   - Fixed in: 0.13.0

### Llama Index (0.9.48 → 0.13.0)
1. **Insecure Temporary File**
   - Severity: Medium
   - Affected: < 0.13.0
   - Fixed in: 0.13.0

2. **Temporary File in Directory with Insecure Permissions**
   - Severity: Medium
   - Affected: < 0.12.3
   - Fixed in: 0.13.0

3. **Command Injection in RunGptLLM**
   - Severity: Critical
   - Affected: < 0.10.13, < 0.1.3
   - Fixed in: 0.13.0

4. **SQL Injection**
   - Severity: Critical
   - Affected: < 0.12.28
   - Fixed in: 0.13.0

### FastAPI (0.109.0 → 0.109.1)
1. **Content-Type Header ReDoS**
   - Severity: Medium
   - Affected: <= 0.109.0
   - Fixed in: 0.109.1

## Code Changes Required

### Updated Import Paths
Due to LangChain and Llama Index major version upgrades, the following import paths were updated:

#### LangChain (vector_store.py, proposal_service.py)
```python
# Old imports
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document

# New imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.schema import Document
```

#### Llama Index (llama_service.py)
```python
# Old imports
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import OpenAI

# New imports
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
```

#### Configuration Changes
- Replaced `ServiceContext` with `Settings` global configuration in Llama Index
- Updated initialization to use `Settings.llm` and `Settings.embed_model`

## Verification

All dependencies have been verified against the GitHub Advisory Database:
- ✅ No vulnerabilities found in updated versions
- ✅ All code syntax verified
- ✅ Import paths updated for compatibility

## Recommendation

Users should update their installations immediately:
```bash
cd backend
pip install -r requirements.txt --upgrade
```

## Additional Security Measures

1. Keep dependencies up to date regularly
2. Monitor security advisories for used packages
3. Use dependabot or similar tools for automated updates
4. Run security scans before deployment
5. Follow least privilege principle for API keys

## Date
January 14, 2026
