David Amaya and Cromwell De Guzman

Our heuristic strategy involves 3 separate checks:

1. **Duplicate Tool Creation Check:** This heuristic prevents redundant tool creation by checking if a tool is already planned to be made in the future. It avoids unnecessary duplication of tasks, improving planning efficiency.

2. **Tool Dependency Check:** This heuristic ensures that the agent does not attempt to make iron tools without first having the prerequisite stone tools. However, this heuristic currently prevents the creation of iron tools altogether, which is unintended.

3. **Efficiency Check:** This heuristic prevents the agent from using inferior tools if better ones are available. It optimizes resource usage and task execution by prioritizing the use of the best available tools.

Although these heuristics attempt to address various aspects of the planning problem, the tool dependency heuristic currently inhibits the creation of iron tools entirely rather than ensuring the presence of stone tools beforehand, indicating a need for further refinement.