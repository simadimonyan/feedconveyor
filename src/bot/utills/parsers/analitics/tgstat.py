from bs4 import BeautifulSoup


class TGStat:

    def get_categories(self):
        soup = BeautifulSoup("https://tgstat.ru/ratings/posts/pt?sort=quotes", 'html.parser')

        return soup.find_all('a', class_='list-group-item list-group-item-action')
    
    def get_filters(self):
        soup = BeautifulSoup(self, 'html.parser')
        return soup.find_all('a', class_='btn font-18 btn-light btn-rounded')

