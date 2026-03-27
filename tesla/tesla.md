Run the Tesla AI agent with the user's query.

Execute this command and print the output verbatim:

```bash
python $SKILL_DIR/tesla_skill.py "$ARGUMENTS"
```

The script handles OAuth authentication, MCP server connection, and system
prompt internally. On first run it will open a browser for Tesla login.
If the command fails, display the error message as-is.
