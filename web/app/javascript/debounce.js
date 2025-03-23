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
    return (...args) => {
        if (shouldWait) return;
        callback(...args);
        shouldWait = true;
        setTimeout(() => {
            shouldWait = false;
        }, delay);
    };
};
