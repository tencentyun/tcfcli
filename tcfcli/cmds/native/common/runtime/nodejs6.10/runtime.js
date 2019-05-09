/*
 * by zalezhang 2018/12/17
 */

var fs = require('fs');
var crypto = require('crypto');


var GLOBAL_FUNCTION_HANDLER = process.argv[2] || process.env.SCF_FUNCTION_HANDLER || 'index:main_handler';
var GLOBAL_FUNCTION_NAME = process.env.SCF_FUNCTION_NAME || "main_handler";
var GLOBAL_EVENT_BODY = process.argv[3] || process.env.SCF_EVENT_BODY ||
    (process.env.DOCKER_USE_STDIN && fs.readFileSync('/dev/stdin', 'utf8')) || '{}';


var GLOBAL_USER_FILE_PATH = '';
var GLOBAL_VERSION = process.env.SCF_FUNCTION_VERSION || '$LATEST';
var GLOBAL_MEM_SIZE = process.env.SCF_FUNCTION_MEMORY_SIZE || '256';
var GLOBAL_TIMEOUT = process.env.SCF_FUNCTION_TIMEOUT || '3';
var GLOBAL_ENVIRON = process.env.SCF_FUNCTION_ENVIRON || '';

var GLOBAL_REQUEST_ID =  uuid();
var GLOBAL_START_TIME = process.hrtime();
var GLOBAL_SOCK = -1;
var GLOBAL_STAGE = 0;


module.exports = {
    init: function() {
        consoleLog('START RequestId: ' + GLOBAL_REQUEST_ID);
        return 0;
    }
    ,
    wait_for_invoke: function() {
        var invokeInfo = [];

        GLOBAL_STAGE += 1;
        switch (GLOBAL_STAGE)
        {
            case 1:
                invokeInfo.cmd = 'RELOAD';
                invokeInfo.context = GLOBAL_USER_FILE_PATH + GLOBAL_FUNCTION_HANDLER;
                break;
            case 2:
                invokeInfo.cmd = 'EVENT';
                invokeInfo.sockfd = GLOBAL_SOCK;
                invokeInfo.event = GLOBAL_EVENT_BODY;
                invokeInfo.context = initContext();
                break;
            default:
                process.exit();
        }

        return invokeInfo;
    },
    log: function (str) {
        //consoleLog(formatSystem(str));
    },
    console_log: function (str) {
        consoleLog(formatConsole(str));
    },
    report_fail: function(stackTrace, typeNum, errType) {
        result = {};

        result['errorCode'] = 1;
        result['errorMessage'] = 'user code exception caught';
        if (stackTrace) {
            result['stackTrace'] = stackTrace;
        }

        reportDone("");
        console.dir(result);
    },
    report_running: function () {
        GLOBAL_START_TIME = process.hrtime();
    },
    report_done: function (resultStr, typeNum) {
        reportDone(resultStr);
    },
}

function initContext() {
    var context = {};
    context['function_version'] = GLOBAL_VERSION;
    context['function_name'] = GLOBAL_FUNCTION_NAME;

    context['time_limit_in_ms'] = GLOBAL_TIMEOUT;
    context['memory_limit_in_mb'] = GLOBAL_MEM_SIZE;

    context['request_id'] = GLOBAL_REQUEST_ID;
    context['environ'] = GLOBAL_ENVIRON;

    return JSON.stringify(context)
}

function reportDone(resultStr) {
    var diffMs = hrTimeMs(process.hrtime(GLOBAL_START_TIME));
    var billedMs = Math.min(100 * (Math.floor(diffMs / 100) + 1), GLOBAL_TIMEOUT * 1000);
    consoleLog('END RequestId: ' + GLOBAL_REQUEST_ID);
    consoleLog([
        'REPORT RequestId: ' + GLOBAL_REQUEST_ID,
        'Duration: ' + diffMs.toFixed(2) + ' ms',
        'Billed Duration: ' + billedMs + ' ms',
        'Memory Size: ' + GLOBAL_MEM_SIZE + ' MB',
        'Max Memory Used: ' + Math.round(process.memoryUsage().rss / (1024 * 1024)) + ' MB',
        '',
    ].join('\t'));

    if (typeof resultStr === 'string') {
        consoleLog('\n' + resultStr);
    }
}

function consoleLog(str) {
    process.stdout.write(str + '\n');
}

function formatConsole(str) {
    return str.replace(/^[0-9TZ:.-]+\t[0-9a-f-]+\t/, '\u001b[34m$&\u001b[0m');
}

function formatSystem(str) {
    return '\u001b[32m' + str + '\u001b[0m';
}

function hrTimeMs(hrtime) {
    return (hrtime[0] * 1e9 + hrtime[1]) / 1e6;
}

function uuid() {
    return crypto.randomBytes(4).toString('hex') + '-' +
        crypto.randomBytes(2).toString('hex') + '-' +
        crypto.randomBytes(2).toString('hex').replace(/^./, '1') + '-' +
        crypto.randomBytes(2).toString('hex') + '-' +
        crypto.randomBytes(6).toString('hex');
}
