function runAfterConditions(callback, cookieName, seconds = 20, scrollPercent = 0.7) {
    let timeMet = false;
    let scrollMet = false;
    const durationMs = seconds * 1000;

    const runCallback = () => {
        if (timeMet && scrollMet) {
            if (!getCookie(cookieName)) {
                setCookie(cookieName, "true", 365);
                callback();
            }
            window.removeEventListener("scroll", throttledOnScroll);
        }
    };

    setTimeout(() => {
        timeMet = true;
        runCallback();
    }, durationMs);

    function onScroll() {
        const scrollTop = window.scrollY;
        const maxScroll = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        if (maxScroll > 0 && scrollTop / maxScroll >= scrollPercent) {
            scrollMet = true;
            window.removeEventListener("scroll", throttledOnScroll);
            runCallback();
        }
    }

    const throttledOnScroll = throttle(onScroll, 200);
    window.addEventListener("scroll", throttledOnScroll);
}
