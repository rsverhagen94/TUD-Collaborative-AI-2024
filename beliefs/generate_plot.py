import csv
import matplotlib.pyplot as plt

files = ['actions2.csv', 'actions3.csv']

timestamps = []
competency_rescue_severelyInjured = []
competency_rescue_mildlyInjured = []
competency_arrival = []
willingness_search = []
willingness_response = []
willingness_rescue = []
scores = []
completenesses = []

name = ''

for i in range(len(files)):
    with open(files[i], 'r') as file:
        reader = csv.DictReader(file, delimiter=';')

        scores.append([])
        completenesses.append([])

        for row in reader:
            name = row['name']
            competency_rescue_severelyInjured.append(float(row['competency_rescue_severelyInjured']))
            competency_rescue_mildlyInjured.append(float(row['competency_rescue_mildlyInjured']))
            competency_arrival.append(float(row['competency_arrival']))
            willingness_search.append(float(row['willingness_search']))
            willingness_response.append(float(row['willingness_response']))
            willingness_rescue.append(float(row['willingness_rescue']))

            scores[i].append(float(row['score']))
            completenesses[i].append(float(row['completeness']))

ticks = range(len(competency_rescue_severelyInjured))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle(name, fontsize=14)

# plot 1

ax1.plot(ticks, competency_rescue_severelyInjured, label='competency_rescue_severelyInjured')
ax1.plot(ticks, competency_rescue_mildlyInjured, label='competency_rescue_mildlyInjured')
ax1.plot(ticks, competency_arrival, label='competency_arrival')
ax1.plot(ticks, willingness_search, label='willingness_search')
ax1.plot(ticks, willingness_response, label='willingness_response')
ax1.plot(ticks, willingness_rescue, label='willingness_rescue')

ax1.set_title('Beliefs')
ax1.set_ylim(-1, 1)
ax1.legend()
ax1.grid(True)

# plot 2

ax3 = ax2.twinx()
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

for i in range(len(files)):
    ax2.plot(range(len(scores[i])), scores[i], label='score_game' + str(i+1), color=colors[i])
    ax3.plot(range(len(scores[i])), completenesses[i], label='completeness_game' + str(i+1), color=colors[i+4])

ax2.set_title('Progress')
ax2.set_xlabel('Tick')
ax2.legend()
ax2.grid(True)

ax3.set_ylim(0, 1)
ax3.legend()

plt.tight_layout()
plt.show()
