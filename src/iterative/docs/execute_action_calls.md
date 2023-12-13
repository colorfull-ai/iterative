I tried running the execute_action_calls form the cli using this command


```bash
iterative execute_action_calls '{"function": "hello_world", "args": {}}'
```

However, since that is not an array you will get an indices error you need to pass it a JSONL format

iterative execute_action_calls '[{"function": "hello_world", "args": {}}]'