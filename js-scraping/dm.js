var msgs = document.getElementsByClassName("DirectMessageItemView_container__wB4Dy")

console.log('Found ' + msgs.length + ' msgs')

skip_user_msgs = false

out_data = []

day = ''

skip_media = false

async function wait_for_next_second()
{
	let now = new Date()
	let ms = now.getMilliseconds();

	// if we are about to tick over to the next second, then wait a little bit
	if (ms >= 950)
	{
		return new Promise(resolve => setTimeout(resolve("wait", 125)))
	}
}

function get_expected_name_date(now, ext)
{
	formattedDate = `${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}${now.getSeconds().toString().padStart(2, '0')}`;
	return 'weverse__' + formattedDate + ext;
}

function get_first_class(e, c)
{
	return e.getElementsByClassName(c)[0]
}

function get_msg_text(e)
{
	text_content = msg.getElementsByClassName("DirectMessageBodyTextView_text__wYswD")[0]
	if (text_content == null)
	{
		text_content = msg.getElementsByClassName("DirectMessageBodyTextView_emoji__OE+ib")[0]
	}

	if (text_content)
	{
		return text_content.textContent
	}
	return ""
}

async function download_msgs()
{
	msg_area = document.getElementsByClassName('DirectMessageRoomView_message_area__Ky585')[0]
	for (msg of msg_area.children)
	{
		await process_msg(msg);
	}

	for (r of out_data)
	{
		console.log(r)
	}

	export_tsv('out.tsv', out_data)
	alert('🍀 fromis_9 🍀 flover 🍀 forever 🍀')
}

function process_msg(msg)
{
	// read day
	if (msg.classList.contains("DirectMessageLineDivderView_divider_text_wrap__ua6da"))
	{
		day = msg.textContent;
		return Promise.resolve("TEXT")
	}

	// otherwise it should be a msg
	is_artist_msg = msg.classList.contains("DirectMessageItemView_-artist__mk8Wp")
	if (skip_user_msgs && !is_artist_msg)
	{
		return Promise.resolve("TEXT")
	}

	time = ''
	time_elem = get_first_class(msg, 'DirectMessageItemView_time__ChpKR');
	if (time_elem != null) time = time_elem.textContent

	text = ''

	img_btn = get_first_class(msg, "DirectMessageBodyImageView_image_button__C53xl")

	audio_btn = get_first_class(msg, "DirectMessageBodyAudioView_viewer_button__3LRyj")

	video_btn = get_first_class(msg, "DirectMessageBodyVideoView_play_button__WOFmB")

	if (img_btn)
	{
		return skip_media ? Promise.resolve("skip") : down_img(img_btn, day, time)
	}
	else if (audio_btn)
	{
		return skip_media ? Promise.resolve("skip") : down_audio(audio_btn, day, time)
	}
	else if (video_btn)
	{
		return skip_media ? Promise.resolve("skip") : down_video(video_btn, day, time)
	}
	else
	{
		down_text(msg, day, time, is_artist_msg)
	}

	// return new Promise(resolve => setTimeout(resolve("Testing", 100))
	return Promise.resolve("TEXT")
	// return new Promise(resolve => {
	// 	resolve("Testing");
	// });
}

// flicking-arrow-next

function down_img(btn, day, time)
{
	btn.click();

    return new Promise(resolve =>
	{
		setTimeout(async function()
		{
			let had_next_arrow = false
			let images = []

			for (i = 0; i < 20; i++)
			{
				let next_arrow = get_first_class(document, "flicking-arrow-next")

				let is_gif = false;
				let img_content = get_first_class(document, 'ImageViewerView_image_content__aWEYs');
				if (img_content != null)
				{
					is_gif = img_content.getAttribute('src').includes('.gif');
				}

				await wait_for_next_second()
				let now = new Date();
				let down_btn = document.getElementsByClassName("ImageViewerView_download_button__9ipF7")[0];
				down_btn.click()

				let will_instant_download = next_arrow == null && !had_next_arrow
				if (will_instant_download)
				{
					// console.log('click down')
					images.push(`${get_expected_name_date(now, is_gif ? '.gif' : '.jpg')}`)
				}
				else
				{
					had_next_arrow = true
				}

				if (had_next_arrow) // click the advanced arrow to download
				{
					await new Promise(resolve => setTimeout(resolve, 1000));
				  	let down_btn_advanced = document.getElementsByClassName("ImageViewerView_layer_button__3VBzE")
					// console.log(down_btn_advanced.length)
				    if (down_btn_advanced.length === 2)
				    {

						// console.log('click advanced')
						await wait_for_next_second()
						let now = new Date();
						down_btn_advanced[1].click()
						images.push(`${get_expected_name_date(now, is_gif ? '.gif' : '.jpg')}`)
				    }
				}

				if (next_arrow == null)
				{
					if (images.length > 0)
					{
						let image_text = `${images.join(',')}`
						// row = [day, time, text]
						let row = { date: day, time: time, image: image_text}
						out_data.push(row)
					}

				    let close_btn = document.getElementsByClassName("ImageViewerView_close_button__9LG7D")[0]
				    close_btn.click()
					resolve("Testing")
					break;
				}
				else
				{
					// wait after clicking the next arrow
					next_arrow.click()
					await new Promise(resolve => setTimeout(resolve, 1000));
				}
			}
		}, 1000)
	})

	// return new Promise(resolve => setTimeout(resolve("Testing", 100))
}

function down_audio(btn, day, time)
{
	btn.click();

    return new Promise(resolve =>
	{
		setTimeout(async function()
		{
			let down_btn = get_first_class(document,"ImageViewerView_download_button__9ipF7");

			await wait_for_next_second()
			let now = new Date();
			down_btn.click()

			let text = `${get_expected_name_date(now,'.mp4')}`
			let row = { date: day, time: time, audio: text}
			out_data.push(row)

		    let close_btn = get_first_class(document,"ImageViewerView_close_button__9LG7D")
		    close_btn.click()
			resolve("Testing")
		}, 1000)
	})

}

function down_video(btn, day, time)
{
	btn.click();

    return new Promise(resolve =>
	{
		setTimeout(async function()
		{
			let down_btn = get_first_class(document,"ImageViewerView_download_button__9ipF7");

			await wait_for_next_second()
			let now = new Date();
			down_btn.click()

			let text = `${get_expected_name_date(now,'.mp4')}`
			let row = { date: day, time: time, video: text}
			out_data.push(row)


		    let close_btn = get_first_class(document,"ImageViewerView_close_button__9LG7D")
		    close_btn.click()
			resolve("Testing")
		}, 1000)
	})
}

function down_text(msg, day, time, is_artist_msg)
{
	text = get_msg_text(msg)
	if (text.length == 0)
	{
		return;
	}

	// console.log(`${day} ${time}: ${text}`)

	if (is_artist_msg)
	{
		let row = {date: day, time: time, text: text}
		out_data.push(row)
	}
	else
	{
		let row = {date: day, time: time, your_text: text}
		out_data.push(row)
	}
}

function get_row_str(row, simple)
{
	if (simple)
	{
		let extra = ''
		if (row.image) extra = `Sent image ${row.image}`
		else if (row.video) extra = `Sent video ${row.video}`
		else if (row.audio) extra = `Sent audio ${row.audio}`
		let text = extra

		let has_your_text = row.your_text != null
		if (row.your_text) // its your text
		{
			text = row.your_text
		}
		else
		{
			text = row.text ? row.text : '';
		}

		let optional_tab = has_your_text ? '\t' : '';

		return `${optional_tab}${row.date} ${row.time}: ${text}`
	}

	let temp_list = []
	temp_list[0] = row.date
	temp_list[1] = row.time
	temp_list[2] = row.text ? `\v${row.text}\v` : ''
	temp_list[3] = row.your_text ? `\v${row.your_text}\v` : ''
	temp_list[4] = row.image ? row.image : ''
	temp_list[5] = row.video ? row.video : ''
	temp_list[6] = row.audio ? row.audio : ''
	return temp_list.join('\t')
}

function save_to_file(filename, csv_file)
{
	let blob = new Blob([csv_file], { type: 'text/tsv;charset=utf-8;' });
	if (navigator.msSaveBlob) { // IE 10+
		navigator.msSaveBlob(blob, filename);
	}
	else
	{
		let link = document.createElement("a");
		if (link.download !== undefined) { // feature detection
			// Browsers that support HTML5 download attribute
			let url = URL.createObjectURL(blob);
			link.setAttribute("href", url);
			link.setAttribute("download", filename);
			link.style.visibility = 'hidden';
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		}
	}
}

function export_tsv(filename, rows)
{
    let csv_file = '';
    for (let i = 0; i < rows.length; i++)
    {
        // csvFile += processRow(rows[i]);
		// console.log(rows[i])
		csv_file += get_row_str(rows[i], false) + '\n';
    }

	save_to_file('dm-log.tsv', csv_file);

	let simple_file = '';
	for (let i = 0; i < rows.length; i++)
	{
		// csvFile += processRow(rows[i]);
		// console.log(rows[i])
		simple_file += get_row_str(rows[i], true) + '\n';
	}

	save_to_file('dm-log.txt', simple_file);
}

download_msgs()

