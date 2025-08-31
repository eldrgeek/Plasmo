# Multi-Agent System for Software Development

A collection of specialized AI agents that work together to develop software projects. Each agent has specific expertise and can be spawned as needed to handle different aspects of development.

## System Overview

### Core Agents
- **Founder Agent**: Acts as CEO/Project Manager, creates project plans and coordinates other agents
- **Recruiter Agent**: Spawns and manages specialist agents based on project needs

### Specialist Agents
- **Product Manager**: Requirements gathering, PRD creation, and project planning
- **Project Setup Agent**: Project scaffolding and development environment setup
- **UI React Engineer**: React frontend development and component libraries
- **UI FastHTML Engineer**: Python-based web interfaces with FastHTML
- **Testing Specialist**: Comprehensive testing and quality assurance
- **Database Administrator**: Database design and management
- **DevOps Engineer**: Deployment and infrastructure
- **UI Designer**: User interface and experience design
- **Technical Writer**: Documentation and guides
- **Marketing Specialist**: Product promotion and content

## Quick Start

### 1. Spawn the Founder Agent
```bash
claude "You are the Founder Agent. Read your instructions from /Users/MikeWolf/Projects/Plasmo/agents/founder_agent.md and begin by analyzing this project: [project description]"
```

**Note**: The agent system is located in `/Users/MikeWolf/Projects/Plasmo/agents/` but can work on peer projects like `/Users/MikeWolf/Projects/DiscordPlus/`

### 2. Spawn the Recruiter Agent
```bash
claude "You are the Recruiter Agent. Read your instructions from /Users/MikeWolf/Projects/Plasmo/agents/recruiter_agent.md and wait for agent requests from the founder."
```

### 3. Use the Agent Spawner Tool
```bash
python /Users/MikeWolf/Projects/Plasmo/agents/agent_spawner.py
```

## Agent Workflow

### Project Planning Flow
1. **Founder Agent** analyzes project requirements
2. **Founder Agent** creates comprehensive project plan
3. **Founder Agent** requests specialist agents from **Recruiter Agent**
4. **Recruiter Agent** spawns appropriate specialist agents
5. **Founder Agent** delegates tasks to specialist agents
6. Specialist agents execute their tasks and report back
7. **Founder Agent** monitors progress and adjusts plan as needed

### Agent Communication
- Agents communicate through the MCP messaging system
- Use `mcp__stdioserver__messages` for inter-agent communication
- Agents can share files and coordinate work
- Founder agent acts as central coordinator

## Agent Templates

### Template Structure
Each agent template includes:
- **Role Definition**: Clear description of agent's purpose and expertise
- **Core Responsibilities**: Key duties and expected deliverables
- **Technical Stack**: Technologies and tools the agent specializes in
- **Working Style**: Communication patterns and development approach
- **Quality Standards**: Expected output quality and formats
- **Tools and Resources**: Available MCP tools and documentation

### Available Templates
- `agent_templates/founder_agent.md`: CEO/Project Manager
- `agent_templates/recruiter_agent.md`: Agent spawner and manager
- `agent_templates/product_manager_agent.md`: Requirements and PRD creation
- `agent_templates/project_setup_agent.md`: Project scaffolding and setup
- `agent_templates/ui_react_engineer.md`: React frontend development
- `agent_templates/ui_fasthtml_engineer.md`: FastHTML web interfaces
- `agent_templates/testing_specialist.md`: Testing and quality assurance

## Usage Examples

### Example 1: Web Application Development
```bash
# 1. Start founder agent
claude "You are the Founder Agent. Read /Users/MikeWolf/Projects/Plasmo/agents/founder_agent.md. 
I need to build a web application with React frontend and FastHTML backend."

# 2. Founder will request UI React Engineer and UI FastHTML Engineer
# 3. Recruiter will spawn appropriate agents
# 4. Agents coordinate to build the application
```

### Example 2: Testing Implementation
```bash
# 1. Founder agent identifies need for testing
# 2. Requests testing specialist from recruiter
# 3. Testing specialist creates comprehensive test suite
```

## Directory Structure

```
agents/
├── README.md                    # This file
├── founder_agent.md             # Founder agent instructions
├── recruiter_agent.md           # Recruiter agent instructions
├── agent_spawner.py             # Utility for spawning agents
├── agent_templates/             # Agent instruction templates
│   ├── ui_react_engineer.md
│   ├── ui_fasthtml_engineer.md
│   ├── testing_specialist.md
│   └── [other specialist templates]
├── active_agents.json           # Registry of active agents
├── logs/                        # Agent activity logs
└── analytics/                   # Performance metrics
```

## Agent Spawning Process

### Using the Agent Spawner
```python
from agent_spawner import AgentSpawner

spawner = AgentSpawner()

# Spawn a React developer
result = spawner.spawn_agent(
    role="ui_react_engineer",
    specialization="component_library",
    project_context="Plasmo browser extension"
)

# List active agents
agents = spawner.list_active_agents()
```

### Manual Agent Spawning
```bash
# Spawn UI React Engineer
claude "You are a UI React Engineer. Read your instructions from /Users/MikeWolf/Projects/Plasmo/agents/agent_templates/ui_react_engineer.md. 
Project context: Building a Plasmo browser extension with React components."
```

## Communication Protocols

### Agent Request Format
```
AGENT REQUEST:
Role: ui_react_engineer
Specialization: component_library
Required Skills: React, TypeScript, Plasmo
Context: Building browser extension UI components
Urgency: high
Expected Duration: 2 weeks
```

### Task Delegation Format
```
TASK DELEGATION TO: [Agent ID]
TASK: Build login component
PRIORITY: High
DEADLINE: 2024-01-20

REQUIREMENTS:
- React component with TypeScript
- Form validation
- Responsive design
- Accessibility compliance

DELIVERABLES:
- LoginComponent.tsx
- Unit tests
- Storybook documentation
```

## Performance Monitoring

### Key Metrics
- Task completion rates
- Code quality scores
- Communication effectiveness
- Timeline adherence
- Agent utilization rates

### Analytics Dashboard
- Agent performance over time
- Project success rates
- Resource utilization
- Quality metrics
- Learning insights

## Best Practices

### For Founder Agents
- Create detailed project plans with clear phases
- Provide sufficient context when requesting agents
- Monitor progress and adjust plans as needed
- Maintain clear communication channels
- Document decisions and rationale

### For Specialist Agents
- Follow established coding standards
- Communicate progress regularly
- Ask for clarification when needed
- Collaborate effectively with other agents
- Maintain high quality standards

### For Recruiter Agents
- Match agents to tasks based on expertise
- Monitor agent capacity and performance
- Optimize resource allocation
- Maintain agent registry accuracy
- Provide agents with necessary resources

## Troubleshooting

### Common Issues
- **Agent spawn failures**: Check template paths and permissions
- **Communication problems**: Verify MCP server connection
- **Performance issues**: Monitor agent workload and capacity
- **Quality concerns**: Review agent instructions and standards

### Debug Commands
```bash
# Check active agents
python agents/agent_spawner.py

# View agent logs
tail -f agents/logs/agent_spawner.log

# Test MCP communication
python -c "from mcp_server import test_communication; test_communication()"
```

## Advanced Features

### Multi-Project Support
- Agents can work on multiple projects
- Context switching between projects
- Resource sharing across projects
- Cross-project learning and optimization

### Learning and Adaptation
- Agent performance tracking
- Continuous improvement based on feedback
- Template updates based on project outcomes
- Knowledge sharing between agents

### Scalability
- Dynamic agent spawning based on workload
- Load balancing across agent instances
- Resource optimization and cleanup
- Performance monitoring and alerts

## Contributing

### Adding New Agent Templates
1. Create new template in `agent_templates/`
2. Follow existing template structure
3. Update agent spawner to recognize new role
4. Add documentation and examples
5. Test agent spawning and functionality

### Improving Existing Agents
1. Analyze agent performance metrics
2. Identify areas for improvement
3. Update agent instructions and capabilities
4. Test changes with real projects
5. Document improvements and best practices

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review agent logs in `logs/` directory
3. Test with simplified scenarios
4. Consult project documentation in `docs/`
5. Check existing agent templates for patterns