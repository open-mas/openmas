# OpenMAS Configuration Loading Issues Detected

The prompt configuration tests have identified the following issues:

1. Project YAML Configuration:
   - The agent_config.prompts property is None even when prompts are defined in the YAML file
   - It appears that project configuration is not properly loading the prompts array

2. Environment Variable Configuration:
   - The PROMPTS environment variable (with JSON data) is not being properly loaded
   - Environment variables for prompts_dir are not overriding the defaults

3. This appears to be a limitation in the configuration loading mechanism, particularly in how nested configuration elements like prompts are handled

Recommended Action:
- Examine the _load_project_config function in src/openmas/config.py
- Check how the AgentConfig loads prompts from different sources
- Ensure proper handling of nested configuration elements
