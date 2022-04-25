// 4000 symbols is the limit.

class ArrayPager {}

// def get_page(items: t.Iterable[str], page_num: int = 1) -> t.Tuple[str, int]:
// items = list(items)
// separator = " **|** "
// max_page_len = 1000
// pages: t.List[str] = []

// length = 0
// start = 0
// for i, item in enumerate(items):
//     delta = len(separator) + len(item)
//     if length + delta > max_page_len:
//         pages.append(separator.join(items[start:i]))
//         start = i
//         length = 0
//     length += delta
// pages.append(
//     separator.join(items[start:]) or "",
// )
// try:
//     page = pages[page_num - 1]
// except IndexError:
//     page = pages[-1]
// return page, len(pages)

const maxPageLength = 80;
const separator = " **|** ";

export function arrayToPages(array: Array<string>): Array<string> {
  let pages: Array<string> = [];
  let page: string = "";

  array.forEach((item) => {
    if (page.length + separator.length + item.length <= maxPageLength) {
      if (page === "") {
        page = item;
      } else {
        page = page + separator + item;
      }
    } else {
      pages.push(page);
      page = item;
    }
  });

  if (page !== "") {
    pages.push(page);
  }

  return pages;
}
