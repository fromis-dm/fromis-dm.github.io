my_data = {}
my_data.data = []

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

        await new Promise(resolve => setTimeout(resolve, 15000));

        if (scroll.scrollHeight === last_height)
        {
            clearInterval(handle);
            return Promise.resolve("Finished")
        }
    }
}

function setup_hook()
{
    if (XMLHttpRequest.prototype.customOpen != null)
    {
        XMLHttpRequest.prototype.open = XMLHttpRequest.prototype.customOpen;
    }

    XMLHttpRequest.prototype.nativeOpen = XMLHttpRequest.prototype.open;

    my_hook = function(data)
    {
        return function(method, url, asynch, user, password)
        {
            this.addEventListener("readystatechange", function() {
                if (this.readyState === 4) { // Ready state 4 means the request is complete
                    if (url.includes('messages') && !url.includes('?after') && !url.includes('?transLang')) // maybe look for fieldSet instead?
                    {
                        let parsed = JSON.parse(this.response);
                        data.data = data.data.concat(parsed['data']);

                        console.log(url);
                        console.log(parsed);
                    }
                }
            });

            return this.nativeOpen(method, url, asynch, user, password);
        };
    }

    XMLHttpRequest.prototype.customOpen = my_hook(my_data);

    XMLHttpRequest.prototype.open = XMLHttpRequest.prototype.customOpen;
}

function remove_hook()
{
    XMLHttpRequest.prototype.open = XMLHttpRequest.prototype.nativeOpen;
}

member_index = 0

function download_json(data)
{
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'comments.json';
    link.click();
}

async function main()
{
    setup_hook()
    let chat_buttons = document.getElementsByClassName('DirectMessageRoomListItemView_chat_button__3Yxoi')
    chat_buttons[member_index].click();
    await new Promise(resolve => setTimeout(resolve, 2000));
    await scroll_top();
    download_json(my_data.data);
    remove_hook();
    alert('Finished scrolling')
    return Promise.resolve();
}

await main()