from human_eval import human_eval_loader

def test_loader():
    ds = human_eval_loader._load_human_eval_data()
    sample = ds[0]
    
    assert len(ds) > 0
    assert sample is not None
    print(sample)