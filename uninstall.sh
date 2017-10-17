service minidns stop
update-rc.d -f minidns remove
systemctl daemon-reload
psql -U postgres -c "DROP DATABASE minidns;"
psql -U postgres -c "DROP USER minidns;"


rm -r /etc/minidns
rm /etc/init.d/minidns