export class User {
  constructor(
    public readonly id: string,
    public readonly userName: string,
    public readonly firstName: string,
    public readonly lastName: string,
    public readonly role: string,
    public readonly apiKey: string
  ) {}

  get avatar() {
    return this.userName.slice(0, 2);
  }

  get isAdminOrOwner() {
    return this.role === "admin" || this.role === "owner";
  }
}
