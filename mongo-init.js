const archive = '/docker-entrypoint-initdb.d/UTEZone.gz';

const admin = db.getSiblingDB('admin');
admin.auth('root', 'root');

print('⏳ Đang restore UTEZone từ', archive);
var exitCode = runProgram(
    '/usr/bin/mongorestore',
    '--host', 'localhost',
    '--port', '27017',
    '-u', 'root',
    '-p', 'root',
    '--authenticationDatabase', 'admin',
    '--nsFrom=UTEZone.*',
    '--nsTo=UTEZone.*',
    '--archive=' + archive,
    '--gzip',
    '--drop',
    '--quiet'
);

if (exitCode !== 0) {
    print('❌ Mongorestore thất bại, exit code:', exitCode);
    quit(exitCode);
}
print('✅ Restore xong database UTEZone');