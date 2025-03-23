const debounceTimers = new Map();
const debounce = (callback, time) => {
    if (debounceTimers.has(callback)) {
        window.clearTimeout(debounceTimers.get(callback));
    }
    const timer = window.setTimeout(() => {
        callback();
        debounceTimers.delete(callback);
    }, time);
    debounceTimers.set(callback, timer);
};

const throttle = (callback, delay) => {
    let shouldWait = false;
    let waitingArgs = null;
    const timeoutFunc = () => {
        if (waitingArgs == null) {
            shouldWait = false;
        } else {
            callback(...waitingArgs);
            waitingArgs = null;
            setTimeout(timeoutFunc, delay);
        }
    };
    return (...args) => {
        if (shouldWait) {
            waitingArgs = args;
            return;
        }
        callback(...args);
        shouldWait = true;
        setTimeout(timeoutFunc, delay);
    };
};
