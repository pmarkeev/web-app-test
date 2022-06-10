# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 18:34:59 2022

@author: MarkeevP
"""

class Yak:
    def __init__(self, name, age, sex):
        self.name = name
        self.age = age
        self.sex = sex
    
    def count_milk(self, days):
        self.milk = 0
        
        for i in range(days):
            if (self.age * 100 + i) < 1000:
                self.milk = self.milk + (50 - (self.age * 100 + i) * 0.03)
        
        return self.milk
        
    # def count_hides(self, days):
    #     self.hides = 0
    #     for i in range(days):
    #         if (self.age * 100 + i) < 1000:
    #             period = math.ceil(8 + self.age + i/100)
    #             if (i % period) == 0 :
    #                 self.hides += 1
    #     return self.hides
    
    def count_hides(self, days):
        if days == 0:
            self.hides = 0
            return self.hides
        last_shave_day = 0
        current_age = self.age
        if self.age > 1:
            self.hides = 1
            last_shaved_age = current_age
        else:
            self.hides = 0
            last_shaved_age = "never shaved"
        day = 0
        while day < days and current_age < 10:
            if (current_age == 1
                    or (current_age > 1
                        and day - last_shave_day >= 8 + current_age)):
                last_shave_day = day
                self.hides += 1 
                last_shaved_age = current_age
            day += 1
            current_age = self.age + day / 100
        return { 'hides' : self.hides, 'last_shaved_age' : last_shaved_age}

    def identify(self):
        print(f'name="{self.name}" age="{self.age}" sex="{self.sex} milk="{self.milk}" hides="{self.hides}"')

class Herd:
    def __init__(self):
        self.labyaks = []
        
    def add_yak(self, yak):
        self.labyaks.append(yak)
            
    def stock_milk(self, days):
        total_milk = 0
        for yak in self.labyaks:
            total_milk += yak.count_milk(days)
        return total_milk
        
    def stock_hides(self, days):
        total_hides = 0
        for yak in self.labyaks:
            total_hides += int(yak.count_hides(days)['hides'])
        return total_hides

    def identify(self, days):
        resulting_list = []
        for yak in self.labyaks:
            temp_dict = {}
            temp_dict['name'] = yak.name
            if yak.age + days / 100 <= 10:
                temp_dict['age'] = yak.age + days / 100
                temp_dict['age-last-shaved'] = yak.count_hides(days)['last_shaved_age']
            else: 
                temp_dict['age'] = 'yak is dead :('
                temp_dict['age-last-shaved'] = 'you cannot shave a dead yak'

            resulting_list.append(temp_dict)
        return resulting_list
