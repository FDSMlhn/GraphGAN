#nohup python3 train.py --model_dir=tmp1/ --bilinear=True --learning_rate=0.01 --dropout=0.3 > result/model_1.txt 2>&1
#nohup python3 train.py --model_dir=tmp2/ --bilinear=True --learning_rate=0.01 > result/model_2.txt 2>&1
#nohup python3 train.py --model_dir=tmp3/ --bilinear=True --learning_rate=0.001 > result/model_3.txt 2>&1
#nohup python3 train.py --model_dir=tmp4/ --learning_rate=0.01 > model_4.txt 2>&1
#nohup python3 train.py --model_dir=tmp5/ --learning_rate=0.001 > model_5.txt 2>&1

#nohup python3 train.py --model_dir=tmp6/ --dim_user_embedding=64 --dim_item_embedding=64  --bilinear=True/ --learning_rate=0.005 > 6.txt 2>&1 &
#nohup python3 train.py --model_dir=tmp7/ --regularizer_parameter=0.001 --bilinear=True/ --learning_rate=0.005 > 7.txt 2>&1 &
#
nohup python3 train.py --model_dir=tmp8/ --bilinear=True/ --regularizer_parameter=0.0005 --learning_rate=0.001 --continue_training=-1 > 8.txt 2>&1 &
#nohup python3 train.py --model_dir=tmp9/  --regularizer_parameter=0.0001  --learning_rate=0.005 > 9.txt 2>&1 &
#nohup python3 train.py --model_dir=tmp10/ --dim_user_embedding=256 --dim_item_embedding=256 --learning_rate=0.01 > 10.txt 2>&1 &
#nohup python3 train.py --model_dir=tmp11/ --dim_user_embedding=256 --dim_item_embedding=256 --learning_rate=0.003 > 11.txt 2>&1 &
nohup python3 train.py --model_dir=tmp12/  --regularizer_parameter=0.0005 --learning_rate=0.001 --continue_training=-1 > 12.txt 2>&1 &

