#! python3
#shebang line^

# Non-learning branch for familiarity's sake

#importing sc2 package
import sc2, random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY,\
 CYBERNETICSCORE, STALKER, ZEALOT

#quick note to self, I'm going to drop camel case for this and use underscores to fit the naming convention..
#.. for functions in the sc2 api

#this is my bot class to fill out with rules
class KipBot(sc2.BotAI):
    def __init__(self):
        self.max_workers = 70
    #this is sort of like the update function in unity or event tick(? correct myself on this later)..
    #..but basically its the main loop for what needs to run
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supply()
        await self.build_vespine()
        await self.expand_base()
        await self.construct_offensive_unit_structures()
        await self.build_army()
        await self.attack()
    
    #start a function to build workers
    async def build_workers(self):
            #shake it up with these lines of code to check the amount probes is less than amount..
            #.. that is 16 per ever nexus 
        if len(self.units(NEXUS)) * 16 > len(self.units(PROBE)):
            # and that the length of probes is less than max workers
            if len(self.units(PROBE)) < self.max_workers:
                #does a loop for the returned nexus that are both ready(are in the process of building)..
                #.. and have no pending work orders or units in queue.
                for nexus in self.units(NEXUS).ready.noqueue:
            #check if you can afford the cost of a probe with the inherited method
                    if self.can_afford(PROBE):
                        #build a probe using the nexus that was returned in the for loop
                        await self.do(nexus.train(PROBE))


    #function for building pylons, supply depots, and overlords
    async def build_supply(self):
        if self.supply_left < 4 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    #function for building on vespine gysers to make them harvestable
    async def build_vespine(self):
        for nexus in self.units.ready:
            #get a list of gysers in range..
            #.. note to self: 25 is just a tad too big of range, builds harvesters on top of secondary location gysers so lets tone it down to 10
            gysers = self.state.vespene_geyser.closer_than(5.0, nexus)
    
            #for the gysters in that list
            for targets in gysers:
                #check if you can afford the gyser harvesting building
                if not self.can_afford(ASSIMILATOR):
                    break

                #try to grab a worker near the location
                worker = self.select_build_worker(targets.position)
                #if you cannot find a worker, break
                if worker is None:
                    break

                # now if there isn't a harvester (in this case an assimilator) close (basically on top) to the gyster (targets)   
                if not self.units(ASSIMILATOR).closer_than(1.0, targets).exists:
                    #then have the worker build a harvester
                    await self.do(worker.build(ASSIMILATOR, targets))    

    #calls expand base if there are less than three bases and can afford a nexus
    async def expand_base(self):
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()

    #This function builds building that deal with offensive units and their upgrading
    #going to just construct this function on a protoss basis..
    #.. because the pylons dictate build locations: will need to change in learning..
    #.. version
    async def construct_offensive_unit_structures(self):

        #checks if theres pylons existing
        if self.units(PYLON).ready.exists:
            #stores a randomly selected pylon and save it as the engergy supply var
            energySupply = self.units(PYLON).ready.random
            
            # if we have a gateway that exists # but not a cybernetics core
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                    # and we can both afford and a cybernetics core and its..
                    #.. not already in the process of building
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        #then build a cybernetics core near our stored pylon
                        await self.build(CYBERNETICSCORE, near = energySupply)
            #but if we have less than 3 gate ways
            elif len(self.units(GATEWAY)) < len(self.units(NEXUS))*2:
                #if we can afford a getway and the total amount of gateways is less than 4
                if self.can_afford(GATEWAY):
                    #then build one
                    await self.build(GATEWAY, near = energySupply)
    
    #this function builds the army
    async def build_army(self):
        #a loop that loops through the available nonque'd gateways
        for portal in self.units(GATEWAY).ready.noqueue:
            if not self.units(CYBERNETICSCORE).ready.exists:
                #lets make some zealots here and try to keep the ratio 50/50..
                #..stalkers to zealots
                if self.can_afford(ZEALOT) and self.supply_left >1:
                #adding another line to check zealot to stalker ratio
                    await self.do(portal.train(ZEALOT))
            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(ZEALOT)) > len(self.units(STALKER)):       
                #if you can afford a stalker and you are not out of supply
                    if self.can_afford(STALKER) and self.supply_left > 1:
                        #build a stalker(s) at a gateway(s)
                        await self.do(portal.train(STALKER))
                else:
                    if self.can_afford(ZEALOT) and self.supply_left > 1:
                        await self.do(portal.train(ZEALOT))

    #a function to handle the assement of available targets to attack..
    # will check if we know either more than one enemy unit or structure..
    # and pick a random structure or unit among them to attack
    #or just go return the enemy start location for attack
    def aquire_target(self, state):
        #check the legnth of known units
        if len(self.known_enemy_units) > 0:
            #return random choice to attack
            return random.choice(self.known_enemy_units)
        #check the length of known enemy structures
        elif len(self.known_enemy_structures) > 0:
            #return a random choice to attack
            return random.choice(self.known_enemy_structures)
        #or else
        else:
            #return the original start location for the enemy 
            return self.enemy_start_locations[0]

    #an attack function
    async def attack(self):
        #check is we have a big enough pool of stalkers to commence an attack with
        if (self.units(STALKER).amount + self.units(ZEALOT).amount) > 30:
            #both loops basically just tell the idle zealots and stalkers to..
            #.. perform attack and to use aquire target to return a target value
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.aquire_target(self.state)))
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.aquire_target(self.state)))



        #check if we have any amount of units between our stalkers and zealots
        elif (self.units(STALKER).amount + self.units(ZEALOT).amount) > 1:
            #if we have any units do loops for stalkers and zealots to attack any known units
            #do a loop for each idle zealot unit
            for unit in self.units(ZEALOT).idle:
                #check to see if we know any units
                if len(self.known_enemy_units) > 0:
                    #tell each unit to attack a known enemy unit
                    await self.do(unit.attack(random.choice(self.known_enemy_units)))

            #do a loop for each idle stalker unit
            for unit in self.units(STALKER).idle:
                #check to see if we know any units
                if len(self.known_enemy_units) > 0:
                    #tell each unit to attack a known enemy unit
                    await self.do(unit.attack(random.choice(self.known_enemy_units)))


    #going to make a function to perform chrono-acceleration casts onto buildings that have a queue
    async def boost_build_speed(self):
        #checks if buildings with queues have the attribute for chrono acceleration and then checks if theres a nexus with enough energy.
        # 
        print('idk why the indent isnt found here')

    #possibly use this to change some of the constants like nexus over to commmand center to make this a little more applicable to more races than on 
    async def set_race_vars(self):
        print('idk why the indent isnt found here')

#calling the run game function, choosing the map with by name via a string, and then choosing the bot and computer as players..
#.. specifying that its a bot, the race is protoss and its going to be run or played by my bot..
#.. basically the same thing with the computer player but instead of specifying a bot we give it a difficulty which is set to easy..
#.. and of course I set realtime to True to make it run in realtime as opposed to as fast as it can.
run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, KipBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime = False)
