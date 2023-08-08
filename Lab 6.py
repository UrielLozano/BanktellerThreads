# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 13:21:41 2023

@author: Cooks
"""
from threading import Semaphore, Thread, Lock
from queue import Queue, Empty
from random import randint
from time import sleep

max_customers_in_bank = 10 # maximum number of customers that can be in the bank at one time
max_customers = 30 # number of customers that will go to the bank today
max_tellers = 3 # number of tellers working today
teller_timeout = 10 # longest time that a teller will wait for new customers

class customer:
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return f"{self.name}"

class teller:
    
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return f"{self.name}"
    
def bankprint(lock, msg):
    with lock:
        print(msg)

def wait_outside_bank(customer, guard, teller_line, printlock):
    bankprint(printlock, f"(C) {customer} is waiting outside the bank.")
    guard.acquire()
    bankprint(printlock, f"<G> Security guard letting {customer} into the bank.")
    bankprint(printlock, f"(C) {customer} getting into line.")
    teller_line.put(customer)
    
def teller_job(teller, guard, teller_line, printlock):
    bankprint(printlock, f"[T] {teller} starting work.")
    while True:
        try:
            x = teller_line.get(customer,teller_timeout)
            bankprint(printlock, f"[T] {teller} is now helping {x}")
            sleep(randint(1, 4))
            bankprint(printlock, f"[T] {teller} is done helping {x}.")
            bankprint(printlock, f"<G> Security guard is letting {x} out of the bank.")
            guard.release()
        except Empty:
            bankprint(printlock, f"[T] Nobody is in line, {teller} is going on break.")        
            break
    
if __name__ == "__main__":
    printlock = Lock()
    teller_line = Queue(maxsize=max_customers_in_bank)
    guard = Semaphore(max_customers_in_bank)
    bankprint(printlock, "<G> Security guard starting their shift")
    bankprint(printlock, "*B* Bank open")
    customers = []
    for x in range(max_customers):
        customers.append(customer(f"customer {x}"))
    cjobs = [Thread(name= x, target = wait_outside_bank, args = (x, guard, teller_line, printlock)) for x in customers]
    for c in cjobs:
        c.start()
    sleep(5)
    bankprint(printlock, "*B* Tellers starting work.")
    tellers = []
    for x in range(max_tellers):
        tellers.append(teller(f"teller {x}"))
    tjobs = [Thread(name= x, target = teller_job, args = (x, guard, teller_line, printlock)) for x in tellers]
    for t in tjobs:
        t.start()
    for t in tjobs:
        t.join()
    bankprint(printlock, "*B* Bank closed.")