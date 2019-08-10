#!/usr/bin/env bash
amazon_hosts=(  'ec2-54-183-153-123.us-west-1.compute.amazonaws.com'
                'ec2-52-53-205-27.us-west-1.compute.amazonaws.com'
                'ec2-13-57-250-10.us-west-1.compute.amazonaws.com'
                'ec2-54-153-59-91.us-west-1.compute.amazonaws.com')

for host_address in ${amazon_hosts[@]}; do
    echo "Copying EXPIRE logs for $host_address"
    scp -i wtf.pem ec2-user@${host_address}:/home/ec2-user/crypto_crawler/logs/expire_deal* ../
    gunzip ../expire_deal*.gz
    cat ../expire_deal* > ${host_address}-expire_deal.log
    rm ../expire_deal*
    echo "Copying ERROR logs for $host_address"
    scp -i wtf.pem ec2-user@${host_address}:/home/ec2-user/crypto_crawler/logs/error* ../
    gunzip ../error*.gz
    cat ../error* > ${host_address}-error.log
    rm ../error*
    echo "Copying FAILED logs for $host_address"
    scp -i wtf.pem ec2-user@${host_address}:/home/ec2-user/crypto_crawler/logs/failed_order* ../
    gunzip ../failed_order*.gz
    cat ../failed_order* > ${host_address}-failed_order.log
    rm ../failed_order*
    echo "Copying PRICE ADJUSTMENT logs for $host_address"
    scp -i wtf.pem ec2-user@${host_address}:/home/ec2-user/crypto_crawler/logs/price_adjustment* ../
    gunzip ../price_adjustment*.gz
    cat ../price_adjustment* > ${host_address}-price_adjustment.log
    rm ../price_adjustment*
done