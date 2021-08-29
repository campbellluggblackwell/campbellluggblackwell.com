    # Find Old rootsweb ID, name, birth and death
    for span in soup.find_all('span', attrs = {'class': 'rwWcGreen'}):
        a_tag = span.next_sibling
        href = a_tag.attrs['href']
        i_number = href.split('/')[5][1:] # Grab only the Innnn portion of the href, then remove the 'I'
        name = a_tag.text
        dates_or_empty = a_tag.next_sibling.string  # Either a birth/death string, or nothing
        born_str = died_str = ''
        if dates_or_empty:
            born = ''
            _sp = dates_or_empty.split('B:')
            if len(_sp)==2:
                _xx = _sp[1].split('D:')
                born = _xx[0]
                if len(_xx)==2:
                    died = _xx[1]
            born = born.replace('.', '').strip()
            born_str = str(born)  # Default, but try to format better
            embed()
            break
            try:
                born_date = datetime.strptime(born, '%d %b %Y')
                born_str = born_date.strftime('%d-%b-%Y')
            except ValueError:
                try:
                    born_date = datetime.strptime(born, '%Y')
                    born_str = born_date.strftime('%Y')
                except:
                    pass
            died = died.strip()
            died_str = str(died)  # default, but try to format better
            try:
                died_date = datetime.strptime(died, '%d %b %Y')
                died_str = died_date.strftime('%d-%b-%Y')