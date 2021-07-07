def get_transactions_dataset():
    
    transactions_file = sim_cfg.transactions_record_file
    
    while not check_file_existance(transactions_file):
        print("Waiting for transactions_file", end='\r', flush = True)
        time.sleep(0.1)
    with open(transactions_file, 'r') as file:
        data=file.read()+"]"
        data=data.replace("'", '"')
        data=data.replace("False", str('"'+"False"+'"'))
        data=data.replace(" True", str(' "'+"True"+'"'))

        return pd.read_json(data)
