UPDATE workflow_entity
SET
  nodes = pg_read_file('/tmp/browser-agent-nodes.json')::jsonb,
  connections = pg_read_file('/tmp/browser-agent-connections.json')::jsonb,
  "updatedAt" = NOW()
WHERE id = 'zfnm0J8fcPqZ6zWu';
