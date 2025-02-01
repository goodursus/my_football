import random

def event_generator(num_events):
    current_time = 0.0
    events = []
    
    for i in range(num_events):
        interval = random.uniform(0.1, 2.0)
        current_time += interval
        print(f"\nСобытие {i+1} сгенерировано через {interval:.2f} сек")

        window_start = current_time - 60
        events = [t for t in events if t > window_start]

        if len(events) >= 10:
            oldest = events[0]
            delay = oldest + 60 - current_time
            current_time += delay
            
            window_start = current_time - 60
            events = [t for t in events if t > window_start]
            delay_info = (True, delay)
        else:
            delay_info = (False, 0.0)

        events.append(current_time)
        
        # Расчет времени выполнения событий в текущем окне
#        window_duration = current_time - window_start
        active_events_duration = current_time - events[0] if events else 0.0

#        print(f"Текущее системное время: {current_time:.2f} сек")
        print(f"Событий в окне: {len(events)} шт")
#        print(f"Длительность 60-секундного окна: {window_duration:.2f} сек")
        print(f"Активные события занимают: {active_events_duration:.2f} сек")
        
        if delay_info[0]:
            print(f"Применена задержка: {delay_info[1]:.2f} сек")
        else:
            print("Задержка не потребовалась")

event_generator(30)