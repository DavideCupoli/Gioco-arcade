<h1 align="center">Venetkens</h1>
<p>
Venetkens is a military strategy game turn based. It has been made in python with arcade library. The aim of the game is to lead a State and invade the other ones.
The map is made by various provinces, whose borders have an hexagonal shape. Every province belongs to a State. The player leads
a State, while others are controlled by BOT.
</p>
<p>
A State can conquer the province of an enemy State by moving its own army:
if the number of the soldiers is bigger than enemy's army one, province's control is transferred to the other State.
Every State can plan a certain number of actions, indicated by the green arrow. The actions are then fulfilled when you pass to the next turn.
States can manage their money and their balance. These values can be negative in the case expenses exceed earnings. 
</p>

**MAIN COMMANDS**

ARROW KEYS: visual movement
<br>
<br>
PLUS/MINUS KEYS: zoom
<br>
<br>
I key: game saving
<br>
<br>
O key: game loading
<br>
<br>
SHIFT: it allows you to select multiple provinces
<br>
<br>
ENLIST BUTTON: it allows you to enlist soldiers in the selected provinces that belong to your State. Select the province where you want to enlist the soldiers and, after you've clicked the button, it will appear a progressive bar that lets select how many troops have to be enlisted; after that, click ENTER to confirm the action. It will appear a green number, which indicates how many
troops have been enlisted.

<br>
<br>
MOVE BUTTON: it allows you to move troops to a province owned by your State or by an enemy State. Select the province of the troop that you want to move; after you've clicked the button, select how many soldiers you want to move; then, select the destination's province. It will appear a red number in the destination's province, that indicates how many troops will come in the next turn.
<br>
<br>
DECLARE WAR BUTTON: it lets to declare war to the State of the selected province.
<br>
<br>
REMOVE BUTTON: it allows you to remove a troop in the case you must decrease the army's mantainment cost. The procedure is the same
of the Enlist command.
<br>
<br>
SPACE: it lets to pass to the next turn.