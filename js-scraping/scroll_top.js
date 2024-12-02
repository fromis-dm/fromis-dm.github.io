async function scroll_top()
{
    scroll = document.getElementsByClassName("DirectMessageRoomContainerView_scroll_content__W5LKA hidable_scrollbar_content")[0]

    let last_height = 0

    // keep trying to scroll every 500ms
    let handle = setInterval(function()
    {
        scroll.scrollIntoView()
    }, 500);

    // if the scroll height hasn't changed for 10s, we are done
    while (true)
    {
        last_height = scroll.scrollHeight

        await new Promise(resolve => setTimeout(resolve, 10000));

        if (scroll.scrollHeight == last_height)
        {
            clearInterval(handle);
            alert('Finished scrolling')
            return Promise.resolve("Finished")
        }
    }
}

scroll_top()