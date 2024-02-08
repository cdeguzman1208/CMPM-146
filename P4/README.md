David Amaya and Cromwell De Guzman

Our heuristic strategy was to simply check if the current tool that you need had already been made.
If you already had the tool, then you would not need to make it again, or else you would get caught
in an infinite loop of checking for the tool.

To do this, we just checked if our current task was already in our list of tasks. If that check ever
returned true, then we would return false and prune that task from the branch.

Also, to maximize time, we decided to pre sort our incoming data from the json file so that when our
methods and the operators were added to our list, they would already be in order of how much time it
takes to produce a certain item.