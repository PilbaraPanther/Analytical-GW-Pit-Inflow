#written by Tim 

import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib 
matplotlib.style.use('ggplot')
from datetime import datetime

#input parameters
#pit effective radius, symbol - rp, unit - m
#zone 1 horizontal K,	symbol - kh unit - m/d
#distributed recharge, 	symbol - W unit - m/d
#zone 2 horizontal K,	symbol - kh2 unit - m/d
#zone 2 vertical K,	symbol - kv, unit - m/d
#pit base, symbol - pitbase, unit - mAHD
#static GWL, symbol - sGWL, unit - mAHD
#anistropy, symbol - ani, unit - na
#depth of ponded area, symbol - hp, unit - m
#height of watertable at radius of influence, symbol - h0, unit - m

    
def pit_inflow():
    df = pd.read_csv('inflow_params.csv', header=0, index_col = 'Parameter')
    print (df)
    #calcs effective pit radius
    width = df.loc['pit width','value']
    length = df.loc['pit length', 'value']
    effectcircradius = math.sqrt(width*length/math.pi)
    print ('effective radius is: ',round(effectcircradius,2), 'm')

    #input parameters for pit inflow 
    hp = 0
    W  = df.loc['distributed recharge','value']
    rp = effectcircradius
    kh1 = df.loc['zone 1 horizontal K','value']
    kh2 = df.loc['zone 2 horizontal K','value']
    kv = df.loc ['zone 2 vertical K','value']
    ani = math.sqrt(kh2/kv)
    pitbase = df.loc['pit base','value']
    sGWL = df.loc['static GWL','value']
    h0 = sGWL - pitbase
          
    print ('Anistrophy is ',round(ani,2))
    
    #create a dictionary of lists with headers roi and pitinflow
    results = {'R0_m':[],'zone_1_pit_inflow_m3/d':[],'drawdown_m':[],'zone_2_pit_inflow_m3/d':[],
                   'total_pit_inflow_m3/d':[],'pit_level_mRL':[]}


    #iterate through r0 values to find r0 equaling h0 from input
    while hp <= h0:
        r0_lower = 0.0001
        r0_upper = 100000
        erra = 100
        margin = 0.0000001
        iter = 0
        while erra > margin and iter < 1000:
            r0_mid = ((r0_upper + r0_lower) / 2)
            h0calc_m = math.sqrt(hp ** 2 + ((W / kh1) * (((r0_mid ** 2) * math.log(r0_mid / rp)) - 
                              ((r0_mid ** 2 - rp ** 2) / 2))))    
            closeenough = math.isclose(h0,h0calc_m,rel_tol=0.000001,abs_tol=margin)
            if h0 >= h0calc_m:
                r0_lower = r0_mid
            else:
                r0_upper = r0_mid  
            
            iter = iter +1  
            
            '''print(r0_upper)
            print('r0 is ',r0_mid)
            print(r0_lower)
            print('h0calc is ', h0calc_m)'''
            
            if r0_mid <= 0.001:
                radiusofinfluence = r0_mid
                zone_1_pit_inflow = 0.0
                zone_2_pit_inflow = 0.0
            else:                
                radiusofinfluence = r0_mid
                zone_1_pit_inflow = W*math.pi*(radiusofinfluence**2-rp**2)
                zone_2_pit_inflow = 4*(kh2/ani)*effectcircradius*(h0-hp)
                    
            total_pit_inflow = zone_1_pit_inflow + zone_2_pit_inflow
            lake_level = pitbase + hp
            
            if closeenough is True:
                break

        # append data into list in dictionary
        results['R0_m'].append(round(radiusofinfluence,2))
        results['zone_1_pit_inflow_m3/d'].append(round(zone_1_pit_inflow,2))
        results['drawdown_m'].append(round(pitbase-hp,2))
        results['zone_2_pit_inflow_m3/d'].append(round(zone_2_pit_inflow,2))
        results['total_pit_inflow_m3/d'].append(round(total_pit_inflow,2))
        results['pit_level_mRL'].append(round(lake_level,2))

        if hp <= h0:
            hp=hp+1

        else:
            break

    #name output file
    K = str(kh1)
    distrutedRecharge =str(W)
    dt = str(datetime.now())
    dt1 = dt.split('.')
    dt2=dt1[0].replace(':','-')
    output = 'K_'+ K + 'Recharge_' + distrutedRecharge+ '_pit_inflow_output_'+ dt2+'.csv'

    #put dictionary into dataframe and then export dataframe to .csv file
    df1=pd.DataFrame.from_dict(results,'columns')
    df1.sort_values(by='R0_m',ascending=True,inplace=True)
    df1.to_csv(output,sep=',',columns=['R0_m','zone_1_pit_inflow_m3/d','zone_2_pit_inflow_m3/d',
                                             'drawdown_m','pit_level_mRL','total_pit_inflow_m3/d'],header=True,index=False)
    #print(df1)
    print ('Success - Pit inflow calculated. Results exported to',output)
    
    #results
    print(df1)
    #chart
    #fig, ax = plt.subplots()
    ax = df1.plot(x='total_pit_inflow_m3/d', y='pit_level_mRL',)
    ax.set_xlabel('Inflow (m3/day)')
    ax.set_ylabel('Pit floor elevation (mRL)')

    plt.show()
    
pit_inflow()
