echo "Start running!"

nohup python3 train.py --use_gpu --model_dir=tmp0/ --learning_rate=0.015 --dim_user_embedding=128 --dim_item_embedding=256 --dim_user_raw=128 --dim_item_raw=256 --dim_user_conv=128 --dim_item_conv=256 --regularizer_parameter=0.001 --batch_size=20000 --continue_training=-1 > 0.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp1/ --learning_rate=0.003 --dropout=0.5 > 1.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp2/ --learning_rate=0.003 --regularizer_parameter=0.001 --continue_training=-1 > 2.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp3/ --learning_rate=0.001 --dropout=0.5 > 3.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp4/ --learning_rate=0.001 --regularizer_parameter=0.001> 4.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp5/ --learning_rate=0.001 --dropout=0.5 --regularizer_parameter=0.001 > 5.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp6/ --learning_rate=0.003 --dropout=0.7 --is_stacked > 6.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp7/ --learning_rate=0.001 --dropout=0.5 --is_stacked --regularizer_parameter=0.001 > 7.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp8/ --learning_rate=0.0005 --dropout=0.7 --regularizer_parameter=0.001 > 8.log & 2>&1 &(kill in one)

#nohup  python3 train.py --model_dir=tmp9/ --learning_rate=0.001 --dropout=0.5 > 9.log & 2>&1 & (kill in zero)
#nohup  python3 train.py --model_dir=tmp10/ --learning_rate=0.003 --regularizer_parameter=0.01 > 10.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp11/ --learning_rate=0.001 --dropout=0.5 --regularizer_parameter=0.0001 > 11.log & 2>&1 & (kill in zero)
#nohup  python3 train.py --model_dir=tmp12/ --learning_rate=0.0001 --regularizer_parameter=0.001> 12.log & 2>&1 &(kill in one, lr too low?)
#nohup  python3 train.py --model_dir=tmp13/ --learning_rate=0.0007 --dropout=0.5 --regularizer_parameter=0.001 > 13.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp14/ --learning_rate=0.0003 --dropout=0.7 --is_stacked > 14.log & 2>&1 &(kill in one)
#nohup  python3 train.py --model_dir=tmp15/ --learning_rate=0.0007 --dropout=0.7 --is_stacked --regularizer_parameter=0.001 > 15.log & 2>&1 &(kill in one)
#nohup  python3 train.py --model_dir=tmp16/ --learning_rate=0.0005 --dropout=0.7 --regularizer_parameter=0.001 > 16.log & 2>&1 & (kill in zero)

#nohup  python3 train.py --model_dir=tmp20/ --learning_rate=0.003 --regularizer_parameter=0.001 --is_Adam > 20.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp21/ --learning_rate=0.003 --regularizer_parameter=0.005 --is_Adam > 21.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp22/ --batch_size=2048 --learning_rate=0.005 --regularizer_parameter=0.001 --is_Adam > 22.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp23/ --batch_size=2048 --learning_rate=0.005 --regularizer_parameter=0.005 --is_Adam > 23.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp24/ --batch_size=2048 --learning_rate=0.01 --regularizer_parameter=0.001 > 24.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp25/ --batch_size=2048 --learning_rate=0.005 --regularizer_parameter=0.001 --is_Adam > 25.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp26/ --learning_rate=0.007 --regularizer_parameter=0.001 --is_Adam > 26.log & 2>&1 &
#nohup  python3 train.py --model_dir=tmp27/ --learning_rate=0.005 --regularizer_parameter=0.001  --batch_size=20000 --continue_training=-1 > 27.log & 2>&1 &

