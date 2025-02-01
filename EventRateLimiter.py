import time
import random
import sys
from collections import deque

def event_handler(event_id):
    print(f"Processing event {event_id} at {time.strftime('%H:%M:%S')}")

def event_generator():
    event_times = deque()
    event_id = 1
    
    while True:
        current_time = time.time()
        
        # Удаляем события, которые произошли более 60 секунд назад
        while event_times and event_times[0] <= current_time - 60:
            event_times.popleft()
        
        # Если событий 10 или больше, ждем
        if len(event_times) >= 10:
            next_available_time = event_times[0] + 60
            planned_delay = max(0, next_available_time - current_time)
            print(f"Rate limit reached. Planned wait time: {planned_delay:.2f} seconds.")
            
            for remaining in range(int(planned_delay), 0, -1):
                sys.stdout.write(f"\rWaiting: {remaining} seconds")
                sys.stdout.flush()
                time.sleep(1)
                
                # Удаляем устаревшие события во время ожидания
                while event_times and event_times[0] <= time.time() - 55:
                    event_times.popleft()
            print("\rWaiting complete.              ")
        
        # Удаляем события, которые могли устареть во время ожидания
        while event_times and event_times[0] <= time.time() - 55:
            event_times.popleft()
        
        # Добавляем текущее событие
        event_times.append(time.time())
        event_handler(event_id)
        
        # Отображаем последние 10 событий
        print("Last 10 event times:", [time.strftime('%H:%M:%S', time.localtime(t)) for t in event_times])
        
        event_id += 1
        
        # Случайная пауза между событиями (0.5 - 3 секунды)
        time.sleep(random.uniform(0.5, 3))

if __name__ == "__main__":
    event_generator()
