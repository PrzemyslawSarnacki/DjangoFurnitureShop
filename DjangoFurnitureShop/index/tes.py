items_list = [1,2,3,1,1,1,1,1,1,1,'ok',3]
for i in range(0,len(items_list),3):
    item_count = items_list[i]
    item_price = items_list[i+1]
    item_name = items_list[i+2]

    print(item_count)
    print(item_price)
    print(item_name)