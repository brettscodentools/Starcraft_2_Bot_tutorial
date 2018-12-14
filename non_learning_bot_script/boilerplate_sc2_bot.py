#! python3
#shebang line^

# Non-learning branch for familiarity's sake

#importing sc2 package
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR

#quick note to self, I'm going to drop camel case for this and use underscores to fit the naming convention..
#.. for functions in the sc2 api

#this is my bot class to fill out with rules
class KipBot(sc2.BotAI):
    #this is sort of like the update function in unity or event tick(? correct myself on this later)..
    #..but basically its the main loop for what needs to run
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_supply()
        await self.build_vespine()
        await self.expand_base()
    
    #start a function to build workers
    async def build_workers(self):
        #does a loop for the returned nexus that are both ready(are in the process of building)..
        #.. and have no pending work orders or units in queue.
        for nexus in self.units(NEXUS).ready.noqueue:
            #check if you can afford the cost of a probe with the inherited method
            if self.can_afford(PROBE):
                #build a probe using the nexus that was returned in the for loop
                await self.do(nexus.train(PROBE))


    #function for building pylons
    async def build_supply(self):
        if self.supply_left < 2 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    #function for building on vespine gysers to make them harvestable
    async def build_vespine(self):
        for nexus in self.units.ready:
            #get a list of gysers in range..
            #.. note to self: 25 is just a tad too big of range, builds harvesters on top of secondary location gysers so lets tone it down to 10
            gysers = self.state.vespene_geyser.closer_than(10.0, nexus)
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

    async def expand_base(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

        

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
    Computer(Race.Terran, Difficulty.Easy)
], realtime = False)
