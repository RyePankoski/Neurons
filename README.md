This is yet another sim. We start by growing a cyclic graph of nodes. Each node has a weight value. They have some color gene inheretence stuff going on but its not relevant to the simulation, its just for looks. 

WE then pick two random nodes and from the start node we send a pulse into the network. The pulse decays as it passes through the nodes.

(Signal strength) = Signal strength * weight. 

If a node is touched by a signal, its weight is increased slightly, so next time a signal touches it, it doesnt lower the signal strength as much. If we find our target node, it sends a signal back along the found path to reinforce this particular path. 
As we pathfind it strongly prefers to travel along stronger nodes, but will sometimes pick a random ndoe to travel along. 

Early in the sim
![image](https://github.com/user-attachments/assets/1b75893d-1d1d-46a5-9a7a-34d05719ca02)


Later in the sim
![image](https://github.com/user-attachments/assets/0490d77e-2702-44e9-b77b-1e27cd380074)

