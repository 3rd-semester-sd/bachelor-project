export enum CuisineType {
  ITALIAN = "italian",
  JAPANESE = "japanese",
  MEXICAN = "mexican",
  INDIAN = "indian",
  FRENCH = "french",
}

export enum MenuCategory {
  APPETIZER = "appetizer",
  MAIN_DISH = "main_dish",
  SIDES = "sides",
  DESSERTS = "desserts",
}

export function enumToPgEnum<T extends Record<string, any>>(
  myEnum: T
): [T[keyof T], ...T[keyof T][]] {
  return Object.values(myEnum).map((value: any) => `${value}`) as any;
}
