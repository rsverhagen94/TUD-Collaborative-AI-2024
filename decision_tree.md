# Decision tree

This overview contains the actions the agent should do for each phase, based on the trust (competance and willingness) it has in the human.

> All *italics printed* actions, I (Vincent) am not sure about , please think about those extra critically when reviewing this.
>
> The **Current Action** describes the code (on a high level) as-is. The **Default Action** is something that I think should happen without trust-differentation, and then the table is used to decide on what to do. 
>
> Some phases are marked with *No trust implementation.*, those phases do not require any trust implementation by my (Vincent) reckoning, mostly since they are interal logic for the behaviour of the agent, without any / much influence from the human agent.

- [Decision tree](#decision-tree)
  - [Intro](#intro)
  - [Find Next Goal](#find-next-goal)
  - [Pick Unsearched Room](#pick-unsearched-room)
  - [Plan Path To Room](#plan-path-to-room)
  - [Follow Path To Room](#follow-path-to-room)
  - [Remove Obstacle If Needed](#remove-obstacle-if-needed)
  - [Enter Room](#enter-room)
  - [Plan Room Search Path](#plan-room-search-path)
  - [Follow Room Search Path](#follow-room-search-path)
  - [Plan Path To Victim](#plan-path-to-victim)
  - [Follow Path To Victim](#follow-path-to-victim)
  - [Take Victim](#take-victim)
  - [Plan Path To Droppoint](#plan-path-to-droppoint)
  - [Follow Path To Droppoint](#follow-path-to-droppoint)
  - [Drop Victim](#drop-victim)


## Intro

**Current action** Print the intro message and wait until the human starts moving

| `Phase.INTRO`   	| High willingness                                           	| Low willingness                                   	|
|-----------------	|------------------------------------------------------------	|---------------------------------------------------	|
| High competence 	| Print intro message and wait until the human starts moving 	| _Print intro message and start moving right away_ 	|
| Low competence  	| Print intro message and wait until the human starts moving 	| _Print intro message and start moving right away_ 	|

## Find Next Goal

**Current Action** For any vicitms that still need rescueing, rescue those that are in `_todo` together, rescue those that not in `_todo` together iff they are `critical` or the human is `weak`, rescue alone otherwise. If no target target victims were found, explore search an unsearched room.

**Default Action** For any vicitms that still need rescueing...

| `Phase.FIND_NEXT_GOAL` 	| High willingness                                                                                                        	| Low willingness                                                                                                      	|
|------------------------	|-------------------------------------------------------------------------------------------------------------------------	|----------------------------------------------------------------------------------------------------------------------	|
| High competence        	| Rescue victims in `_todo` first, and do so alone, then search rooms  and then search victims that are not in _`todo`    	| Rescue victims in `_todo` first, and do so alone, then search victims that are not in `_todo` and then search rooms  	|
| Low competence         	| Rescue victims in `_todo` first, and do so toghether, then search rooms and then search victims that are not in `_todo` 	| Rescue victims in `_todo` first, and do so alone, then search rooms  and then search victims that are not in _`todo` 	|

## Pick Unsearched Room

**Current Action** Determine the unsearched areas, if all areas are searched, but the game not finished, reset the list. Determine the closest unsearched room and pick that.

**Default Action** Determine the unsearched areas, if all areas are searched, but the game not finished, reset the list.

| `Phase.PICK_UNSEARCHED_ROOM` 	| High willingness                                     	| Low willingness                                                                                          	|
|------------------------------	|------------------------------------------------------	|----------------------------------------------------------------------------------------------------------	|
| High competence              	| Determine the closest unsearched room and pick that. 	| *Add the rooms the agent says are empty to the list with a probabilty of the inverted willingsness. Determine the closest unsearched room and pick that.* 	|
| Low competence               	| Determine the closest unsearched room and pick that. 	| *Add the rooms the agent says are empty to the list with a probabilty of the inverted willingsness. Determine the closest unsearched room and pick that.* 	|

## Plan Path To Room

**Current Action** If the human found a victim in a room, navigate to that room, otherwise navigate to the room that was chosen.

| `Phase.PLAN_PATH_TO_ROOM`	| High willingness                                                     	| Low willingness               	|
|--------------------------	|----------------------------------------------------------------------	|-------------------------------	|
| High competence          	| Navigate to the room the human found a victim in, or the chosen room 	| _Navigate to the chosen room_ 	|
| Low competence           	| Navigate to the room the human found a victim in, or the chosen room 	| _Navigate to the chosen room_ 	|

## Follow Path To Room

**Current Action** If the human rescued the victim or searched the room while going there, choose a next goal. If the path is blocked by an obstacle, remove if needed.

*No trust implementation.*

## Remove Obstacle If Needed

**Current Action** If the obstacle is a rock, wait for instruction from the human, if they say continue, search a new room, if they say remove, wait for them. If the obstacle is a tree, wait for instruction from the human, if they say continue, search a new room, if they say remove, remove the tree. If the obstacle is a stone, wait for instruction from the human, if they say continue, search a new room, if they say remove alone, remove the stone, if they say remove together wait for them.

**Default Action** Same as current action, but with the changes from the table below.

| `Phase.REMOVE_OBSTACLE_IF_NEEDED` 	| High willingness               	| Low willingness                          	|
|-----------------------------------	|--------------------------------	|------------------------------------------	|
| High competence                   	| 	| _Remove stones alone always, wait for rocks with a timer_ 	|
| Low competence                    	|   | _Remove stones alone always, wait for rocks with a timer_ 	|

## Enter Room

**Current Action** If the target victim was rescued or found in another room or this area was just searched by the human and nothing was found, find next goal. Otherwise, plan to search the room.

**Default Action** Same as current action, but with the changes from the table below.

| `Phase.ENTER_ROOM                 ` 	| High willingness 	| Low willingness                                                                    	|
|-----------------------------------	|------------------	|------------------------------------------------------------------------------------	|
| High competence                   	|                  	| If the human said they just searched this room and found nothing, search it again. 	|
| Low competence                    	|                  	| If the human said they just searched this room and found nothing, search it again. 	|

## Plan Room Search Path

**Current Action** Efficiently search all tiles in the room (done with a helper function).

*No trust implementation.*

## Follow Room Search Path

**Current Action** If a victim was found, ask the human what to do. If no victim was found where the human said it'd be, message that. Act based on the humans response (remove together, remove alone or continue).

| `Phase.FOLLOW_ROOM_SEARCH_PATH` 	| High willingness                         	| Low willingness                                                                          	|
|---------------------------------	|------------------------------------------	|------------------------------------------------------------------------------------------	|
| High competence                 	| Do what the human says and wait for them 	| If victim is mildly injured, always remove alone. Wait for remove together with a timer. 	|
| Low competence                  	| Do what the human says and wait for them 	| If victim is mildly injured, always remove alone. Wait for remove together with a timer. 	|

## Plan Path To Victim

**Current Action** Navigate to the victim

*No trust implementation.*

## Follow Path To Victim

**Current Action** If the human rescued the victim, find next goal. Move to the victim and take it.

*No trust implementation.*

## Take Victim

**Current Action** If remove together, then wait for the human. When the victim is picked up, find next goal. If rescue alone, pick it up and plan the path to the dropzone.

| `Phase.TAKE_VICTIM` 	| High willingness                                        	| Low willingness                                                      	|
|---------------------	|---------------------------------------------------------	|----------------------------------------------------------------------	|
| High competence     	| Wait for the human then rescue together or rescue alone 	| Wait for the human with a timer then rescue together or rescue alone 	|
| Low competence      	| Wait for the human then rescue together or rescue alone 	| Wait for the human with a timer then rescue together or rescue alone 	|

## Plan Path To Droppoint

**Current Action** Navigate to the droppoint

*No trust implementation.*

## Follow Path To Droppoint

**Current Action** Communicate the vicitim is being moved, move to the droppoint and drop it there.

*No trust implementation.*

## Drop Victim

**Current Action** Communicate the victim is dropped, if rescued alone. Find next goal.

*No trust implementation.*

