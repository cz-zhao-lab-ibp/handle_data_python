from matplotlib import pyplot as plt

a = [1,2,3,4]
b = [2,3,4,5]
c = [4,3,2,1]

fig = plt.figure()
# sub_fig1 = fig.add_subplot(111)
# sub_fig1.plot(a,b)
# sub_fig1.set_ylabel('Label1')
# sub_fig1.set_xlabel('Xlabel1')

# sub_fig2 = sub_fig1.twinx()
# sub_fig2.plot(a,c)
# sub_fig2.set_ylabel('Label2')

plt.plot(a,b)
plt.twinx()
plt.plot(a,c)

plt.show()